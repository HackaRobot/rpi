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
end_headers()
print(pymjpeg.boundary)

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
xmittime = 0
while time.time() < endtime:
    try:
        elapsed = time.time() - xmittime
        newtime = os.lstat(filename).st_mtime
        #sys.stderr.write("newtime={0} elapsed={1}\n".format(newtime, elapsed))
        # Send a pic every 5 seconds, no matter what
        if newtime == mtime and (elapsed < 5):
            #sys.stderr.write("newtime == mtime. Sleeping..\n")
            time.sleep(1)
            continue

        #sys.stderr.write("Xmitting..\n")
        mtime = newtime

        # Send per-image headers
        for k, v in pymjpeg.image_headers(filename).items():
            send_header(k, v)
        end_headers()

        # Send image  binary
        for chunk in pymjpeg.image(filename):
            sys.stdout.write(chunk)

        # Send boundary after image
        print(pymjpeg.boundary)

        xmittime = time.time()
        #sys.stderr.write("Flusing....\n")
        sys.stdout.flush()
    except RuntimeError:
        #sys.stderr.write("Sleeping..\n")
        time.sleep(1)

#sys.stderr.write("Done.\n")
#newtime = os.lstat(filename).st_mtime
#sys.stderr.write("Final newtime={0}\n".format(newtime))
