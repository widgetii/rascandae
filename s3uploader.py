
from constants import BUCKET_NAME, AWS_ACCESS_KEY,AWS_SECRET_KEY,PICFOLDER, MIN_IDLE_TIME_BEFORE_UPLOAD, REPORT_EMAIL, SMTP_SERVER, REPORT_ON_FREE_SPACE_LESS_THAN, DELETE_ON_FREE_SPACE_LESS_THAN
from utils import filename_by_guid
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from state import Picture, Session
import datetime
import time
import os
import lockfile
import logging
from logging.handlers import SMTPHandler

logger = logging.getLogger('rascandae')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('s3upload.log')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)



sh = SMTPHandler(SMTP_SERVER, 'report@' + os.uname()[1],[ REPORT_EMAIL], 'Feed tranform report')

sh.setLevel(logging.WARNING)



def check_if_idle():

    """
    Should check if there is no shot processing currently taking place.
    Should check if last shot was taken at least 20 minutes ago.
    By checking ctime of PICTURES folder (IMPORTANT this will break on WINDOWS as ctime would mean creation time)

    
    """

    idle_flag =time.time()-os.path.getctime(PICFOLDER) > MIN_IDLE_TIME_BEFORE_UPLOAD
    
    logger.debug("Checking if system is idle")

    take_shot_lock = lockfile.FileLock('take_shot')

    if idle_flag and (not take_shot_lock.is_locked()):

        logger.debug("System is idle")
    
        return True

    else:

        logger.debug("System is not idle")
        
        return False



def upload(picture,session, bucket):

    '''
    This functions find file by guid and uploads it at s3


    '''

    # We form prefix aka folder as YYYY/MM/ from ctime of picture file in question

    cdate = datetime.date.fromtimestamp(os.path.getctime(picture.filename))


         
    key_prefix="%s/%s/" %(cdate.year,cdate.month)
    
    k = Key(bucket)
         
    k.key = key_prefix+os.path.basename(picture.filename)

    logger.debug("Uploading %s to %s",picture.filename,k.key)
    
    ustart = datetime.datetime.now()
    k.set_contents_from_filename(picture.filename)
    ufinish = datetime.datetime.now()

    logger.debug("Finished uploading %s to %s",picture.filename,k.key)
     
    
    picture.mark_uploaded(ustart,ufinish)

    if os.path.exists(picture.filename):

        logger.debug("Deleting file %s", picture.filename)
        os.remove(picture.filename)
    session.add(picture)

    
def sorted_ls(path):
    mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
    return list(sorted(os.listdir(path), key=mtime))
    


if __name__ == "__main__":

    session = Session()

    try:
        fst = os.statvfs(PICFOLDER)
        free_space = fst.f_frsize * fst.f_bavail

        if free_space < REPORT_ON_FREE_SPACE_LESS_THAN:

            logger.warning("There is only %d mb left, Recommended is %d", free_space / 1024 / 1024, REPORT_ON_FREE_SPACE_LESS_THAN / 1024 / 1024)

        if free_space < DELETE_ON_FREE_SPACE_LESS_THAN:
            logger.warning("Deleting picture files as system running out of space.  You can find list of deleted files in s3uploader.log")

            for filename in sorted_ls(PICFOLDER):
                fst = os.statvfs(PICFOLDER)
                free_space = fst.f_frsize * fst.f_bavail

                if free_space > DELETE_ON_FREE_SPACE_LESS_THAN:

                    break

                else:

                    logger.info('Deleting %s to free up some space',  filename)

                    os.remove(os.path.join(PICFOLDER, filename))
                


    except Exception, e:

        logger.warning("Can't determine free space, or something else. Service may be deteriorated.  Check paths Error %s", str(e))

    unuploaded =session.query(Picture).filter(Picture.uploaded ==False).all()

    logger.debug('Found %d pictures to upload in database', len(unuploaded))

    
    for pic in unuploaded:

        if check_if_idle():
            if os.path.exists(pic.filename): 
                conn = S3Connection(AWS_ACCESS_KEY,AWS_SECRET_KEY)
                bucket = conn.get_bucket(BUCKET_NAME)
                upload(pic,session,bucket)
                session.commit()
            else:
                logger.debug("Couldn't find %s, Removing record from db" )
                try:
                    
                    session.delete(pic)
                    session.commit()
                except Exception, e:
                    logger.debug('Failed to remove pic.  Error %s', str(e))
                 
        else:

            logger.debug("Exiting as system is busy")

            break
            