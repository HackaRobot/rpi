#!/usr/bin/env python

import cgi
import cgitb
import pymjpeg
import sys
import time, os
from glob import glob

def send_header(key, value):
    print key + ': ',
    print value

def end_headers():
    print

def send_response(code):
    print "HTTP/1.0 {0} OK\r\n".format(code),

#send_response(200)
# Response headers (multipart)
for k, v in pymjpeg.request_headers().items():
    send_header(k, v)

# Multipart content
duration = 20
form = cgi.FieldStorage()
if "duration" in form:
    durationstr = form['duration'].value
    d = int(durationstr)
    if d > 5 and d < 60:
        duration = d
endtime = time.time() + duration
filename = "image.jpg"
mtime = 0
while time.time() < endtime:
    try:
        newtime = os.lstat(filename).st_mtime
        #sys.stderr.write("newtime={0}\n".format(newtime))
        if newtime == mtime:
            #sys.stderr.write("newtime == mtime. Sleeping..\n")
            time.sleep(1)
            continue
        mtime = newtime

        # Send boundary
        end_headers()
        print(pymjpeg.boundary)
        end_headers()

        # Send headers
        for k, v in pymjpeg.image_headers(filename).items():
            send_header(k, v)
        end_headers()

        # Part binary
        for chunk in pymjpeg.image(filename):
            sys.stdout.write(chunk)
            pass

        #sys.stderr.write("Flusing....\n")
        sys.stdout.flush()
    except RuntimeError:
        #sys.stderr.write("Sleeping..\n")
        time.sleep(1)

#sys.stderr.write("Done.\n")
#newtime = os.lstat(filename).st_mtime
#sys.stderr.write("Final newtime={0}\n".format(newtime))
