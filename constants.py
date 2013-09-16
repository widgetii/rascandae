import os
EXTENSION = '.jpg'
TIMEDELAY = 1

AWS_ACCESS_KEY='AKIAILM4W32R7UFBKHWA'

AWS_SECRET_KEY = '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'


BUCKET_NAME='aplix.images'

PICFOLDER = './pictures'

REPORT_EMAIL = 'lyubimov.denis@gmail.com'

SMTP_SERVER = 'noc.aplix.ru'

if 'RASCANDAE_WORKING_DIR' in os.environ:
    
    WORKING_DIRECTORY = os.environ['RASCANDAE_WORKING_DIR']

else:

    WORKING_DIRECTORY ='/home/pi/rascandae/'

MIN_IDLE_TIME_BEFORE_UPLOAD = 1200 # Should be 1200= 20 min according to specs if less than that it's probably for testing