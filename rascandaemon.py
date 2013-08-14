"""
This daemon should do following

Every TIMEDELAY seconds look for file take_shot.

If there is such file, then it should look for *.temp file and then
it should create taking_shot lock save camera image in
* named file, after that it should delete *.request file and release take_shot lock by deleting that file.


"""

import daemon
import subprocess
import os
import glob
import logging
import lockfile
import time
import datetime
import argparse

logger=logging.getLogger('rascandae')
logger.setLevel(logging.DEBUG)

from constants import EXTENSION,TIMEDELAY, WORKING_DIRECTORY
from state import Picture, Session
from utils import filename_by_guid

def capture_into_filename(filename):
    '''
    Capturing image into filename
    '''

    logger.debug("Trying to save image to %s", filename)

    if os.path.exists(filename):
        logger.warning("File %s already exists it will be overwritten", filename)
        
    subprocess.check_output(['sudo', 'gphoto2', ' -- force-overwrite --capture-image-and-download', '--filename', filename])

def check_request():

    requests =glob.glob('*.request')

    logger.debug('Found following requests %s',str(requests))

    return len(requests)>0

def get_request_name():

    '''
    Looking for *.request files and returning * string
    '''

    request_files = glob.glob('*.request')

    if len(request_files) ==1:

        request = request_files[0].split('.request')[0]

        logger.info('Found %s request', request)

        return request

    elif len(request_files) ==0:

        return "DEFAULT"

        logger.warning('There is no request file. Returning DEFAULT as filename')

    else:

        logger.warning('There are multiple request files. Returning DEFAULT as filename')

        return "DEFAULT"
        
def clean_up():

    '''
    Removing all request files and clearing take_shot lock
    '''


    requests = glob.glob('*.request')

    if len(requests) == 1:

        logger.debug("Removing %s file", requests[0])

        os.remove(requests[0])

    elif len(requests) >1:

        logger.warning("There are multiple requsts files. Removing all")

        for req in requests:
            logger.debug("Removing %s file", req)
            
            os.remove(req)
    else:

        logger.warning("Couldn't find request file to remove")


def main():

    take_shot_lock = lockfile.FileLock('take_shot')


    session = Session()
    while True:

        time.sleep(TIMEDELAY)

        try:

            if check_request():
                
                if  not take_shot_lock.is_locked():


                    with take_shot_lock:

                        request_name = get_request_name()

                        cstart = datetime.datetime.now()
                        filename=filename_by_guid(request_name)
                        capture_into_filename(filename)
                        cfinish = datetime.datetime.now()

                        pic = Picture(request_name,cstart,cfinish)
                        session.add(pic)
                        session.commit()
                        
        except Exception,e:

            logger.error(e)
    


if __name__ =="__main__":
    
    parser = argparse.ArgumentParser()

    parser.add_argument("--daemonize", dest='daemonize', action="store_true" , default=False)

    args = parser.parse_args()

    if args.daemonize:
        fh = logging.FileHandler('rascandae.log')
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        
        with daemon.DaemonContext(files_preserve=[fh.stream,], working_directory=WORKING_DIRECTORY):
        
            main()

    else:

        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        logger.addHandler(ch)
        logger.info("Starting Raspberry Pi Canon Camera Daemon")
        main()
    

            
        
    
    