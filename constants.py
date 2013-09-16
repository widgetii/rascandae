import os
EXTENSION = '.jpg'
TIMEDELAY = 1

AWS_ACCESS_KEY='AKIAILM4W32R7UFBKHWA'

AWS_SECRET_KEY = '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'


BUCKET_NAME='aplix.images'

PICFOLDER = './pictures'

REPORT_EMAIL = 'post@aplix.ru'

SMTP_SERVER = 'noc.aplix.ru'

REPORT_ON_FREE_SPACE_LESS_THAN =  500 * 1024 * 1024 # In bytes Default is 500mb

DELETE_ON_FREE_SPACE_LESS_THAN = 100 * 1024 * 1024 # Defaulst is 100mb

if 'RASCANDAE_WORKING_DIR' in os.environ:
    
    WORKING_DIRECTORY = os.environ['RASCANDAE_WORKING_DIR']

else:

    WORKING_DIRECTORY ='/home/pi/rascandae/'

MIN_IDLE_TIME_BEFORE_UPLOAD = 1200 # Should be 1200= 20 min according to specs if less than that it's probably for testing