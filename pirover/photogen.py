#!/usr/bin/python

# This script runs inside the RPi and listens for rover commands.
# It also takes pictures and uploads to URL.

import time
import picamera
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import select
import sys

UPLOAD_URL = "http://sverige.freeshell.org:8000/cgi-bin/upload.py"

def process_photo(camera):
    print "Capturing image.."
    camera.capture('image.png', resize=(320, 240))
    print "Done. Now uploading it."


    # Start the multipart/form-data encoding of the file "image.png"

    # headers contains the necessary Content-Type and Content-Length
    # datagen is a generator object that yields the encoded parameters
    datagen, headers = multipart_encode({"image": open("image.png", "rb")})

    # Create the Request object
    request = urllib2.Request(UPLOAD_URL, datagen, headers)
    # Actually do the request, and get the response
    resp = urllib2.urlopen(request).read()
    # Ignore response.

camera = picamera.PiCamera()
camera.vflip = True
camera.hflip = True
register_openers()
poll = select.poll()
poll.register(0, select.POLLIN)
time.sleep(2) # Allow for camera warm-up

process_photo(camera)
time.sleep(3)
evts = poll.poll(0)
while len(evts) == 0:
    process_photo(camera)
    time.sleep(3)
    evts = poll.poll(0)

camera.close()
