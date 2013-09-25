from flask import Flask,url_for,redirect
from utils import filename_by_guid
from constants import EXTENSION
import lockfile
import glob
import time
import os

PORT = 80


app = Flask(__name__,static_url_path='/static',static_folder="./pictures/")

app.debug=False

@app.route('/take/<guid>')
def make_photo(guid):

    fl = lockfile.FileLock('take_shot')
    el = lockfile.FileLock('error')

    if el.is_locked():

        return "ERROR"

    if not fl.is_locked():

        with fl:

            with open(guid +'.request','w') as request_file:

                request_file.write(' ')
            
        return "OK"

    else:

        return "BUSY"

@app.route('/get/<guid>')
def get_picture(guid):

    return redirect(url_for('static',filename=guid+EXTENSION))

@app.route('/now')
def get_picture_now():

    guid='now'
    
    if os.path.exists(filename_by_guid(guid)):
        os.remove(filename_by_guid(guid))


    fl = lockfile.FileLock('take_shot')

    if not fl.is_locked():

        with fl:

            with open(guid +'.request','w') as request_file:

                request_file.write(' ')


    return """<html>
     <head>
    <script>
    function redirect(){
    window.location='/static/now.jpg'
    }
    </script>
    </head>
    <body onLoad="setTimeout('redirect()', 7000)">
<h2>Wait 7s while image is updated</h2></body><html>

    """



@app.route('/')
def status():


    fl = lockfile.FileLock('take_shot')

    if fl.is_locked():

        requests = glob.glob('*.request')

        if len(requests) ==1:

            return """<html><body>

            Processing %s request
            
            </body></html>
            

            """ % requests[0].split('.request')[0]
        else:

            return "Something wrong, \n requests list is: \n %s " % (str(requests),)

    else:

        return "<html><body>Idle</body></html>"

    
if __name__ == "__main__":
    el = lockfile.FileLock('error')

    if el.is_locked():

        print "Found error lock.  Clearing it"

        el.break_lock()

        if el.is_locked():

            raise NameError("Couldn't break error lock.  Exiting'")

        else:

            print "Cleared lock"

    print "Starting webserver"

    app.run(host='0.0.0.0',port = PORT)