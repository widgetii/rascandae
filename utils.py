from constants import EXTENSION, PICFOLDER
import os

def filename_by_guid(guid):

    return os.path.join(PICFOLDER,guid+EXTENSION)
    