
from constants import BUCKET_NAME, AWS_ACCESS_KEY,AWS_SECRET_KEY
from utils import filename_by_guid
from boto.s3.connection import S3Connection
from boto.s3.key import Key
from state import Picture, Session
import datetime




conn = S3Connection(AWS_ACCESS_KEY,AWS_SECRET_KEY)
bucket = conn.create_bucket(BUCKET_NAME)


def check_if_idle():

    """
    Should check if there is no shot processing currently taking place.
    Should check if last shot was taken at least 20 minutes ago.
    """

    return True



def upload(picture,session):

    '''
    This functions find file by guid and uploads it at s3

    '''

    k = Key(bucket)
    k.key = picture.guid

    ustart = datetime.datetime.now()
    k.set_contents_from_filename(picture.filename)
    ufinish = datetime.datetime.now()

    picture.mark_uploaded(ustart,ufinish)

    session.add(picture)

    
    


if __name__ == "__main__":

    session = Session()
    for pic in Picture.query(Picture.uploaded ==False).all():

        if check_if_idle():
            upload(pic,session)
            session.commit()
        else:

            break
            