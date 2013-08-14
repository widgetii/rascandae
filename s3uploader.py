
from constants import BUCKET_NAME, AWS_ACCESS_KEY,AWS_SECRET_KEY,PICFOLDER, MIN_IDLE_TIME_BEFORE_UPLOAD
from utils import filename_by_guid
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from state import Picture, Session
import datetime
import time
import os
import lockfile
import logging

logger = logging.getLogger('rascandae')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('s3upload.log')
fh.setLevel(logging.DEBUG)
logger.addHandler(fh)





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



    
    picture.mark_uploaded(ustart,ufinish)

    session.add(picture)

    
    


if __name__ == "__main__":

    session = Session()

    unuploaded =session.query(Picture).filter(Picture.uploaded ==False).all()

    logger.debug('Found %d pictures to upload', len(unuploaded))

    
    for pic in unuploaded:

        if check_if_idle():
            conn = S3Connection(AWS_ACCESS_KEY,AWS_SECRET_KEY)
            bucket = conn.get_bucket(BUCKET_NAME)
            upload(pic,session,bucket)
            session.commit()
        else:

            logger("Exiting as system is busy")

            break
            