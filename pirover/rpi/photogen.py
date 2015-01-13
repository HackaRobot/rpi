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
import io
from PIL import Image, ImageDraw
from datetime import datetime

# CUSTOMIZE: Replace with your URL.
UPLOAD_URL = "http://localhost:8000/cgi-bin/upload.cgi"

def add_text(stream):
    image = Image.open(stream)
    draw = ImageDraw.Draw(image)
    draw.line([(42, 240),(80, 200)], width=2, fill=128)
    draw.line([(207, 240),(190, 190)], width=2, fill=128)
    now = datetime.now()
    str = now.strftime("%H:%M")
    draw.text((0, 0), str)
    #PIL cannot save to a stream, so write to a file and read it back.
    image.save("tmp.jpg", format="jpeg")
    fp = open("tmp.jpg", "rb")
    return fp

def process_photo(camera, text=False):
    #print "Capturing image.."
    ostream = io.BytesIO()
    camera.capture(ostream, format='jpeg', resize=(320, 240), use_video_port=True)
    #print "Done. Now uploading it..."
    ostream.seek(0)

    if text:
        ostream = add_text(ostream)

    # Start the multipart/form-data encoding of the file "image.jpg"

    # headers contains the necessary Content-Type and Content-Length
    # datagen is a generator object that yields the encoded parameters
    datagen, headers = multipart_encode({"image": ostream})

    # Create the Request object
    request = urllib2.Request(UPLOAD_URL, datagen, headers)
    # Actually do the request, and get the response
    resp = urllib2.urlopen(request).read()
    #print "Upload done."
    # Ignore response.
    ostream.close()

endtime = time.time() + 60 # At most for 1 min.
camera = picamera.PiCamera()
camera.vflip = True
camera.hflip = True
register_openers()
poll = select.poll()
poll.register(0, select.POLLIN)
time.sleep(2) # Allow for camera warm-up

process_photo(camera)
evts = poll.poll(0)
while len(evts) == 0 and time.time() < endtime:
    process_photo(camera)
    evts = poll.poll(0)

print "Final photo.."
process_photo(camera, text=True)
camera.close()
print "Done."
