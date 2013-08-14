import os
EXTENSION = '.jpg'
TIMEDELAY = 1

AWS_ACCESS_KEY=''

AWS_SECRET_KEY = ''


BUCKET_NAME='rascandaedemo'

PICFOLDER = './pictures'

if 'RASCANDAE_WORKING_DIR' in os.environ:
    
    WORKING_DIRECTORY = os.environ['RASCANDAE_WORKING_DIR']

else:

    WORKING_DIRECTORY ='/home/pi/rascandae/'
