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

def add_text(stream):
    #print "Adding text"
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

def capture_photo(camera):
    #print "Capturing image.."
    ostream = io.BytesIO()
    camera.capture(ostream, format='jpeg', resize=(320, 240), use_video_port=True)
    #print "Done. Now uploading it..."
    ostream.seek(0)

    return ostream

def upload_photo(ostream):

    # Start the multipart/form-data encoding of the file "image.jpg"

    # headers contains the necessary Content-Type and Content-Length
    # datagen is a generator object that yields the encoded parameters
    datagen, headers = multipart_encode({"image": ostream})

    # Create the Request object
    request = urllib2.Request(UPLOAD_URL, datagen, headers)
    # Actually do the request, and get the response
    try:
        resp = urllib2.urlopen(request).read()
        #print "Upload done."
    except:
        print "Could not open URL:" + UPLOAD_URL
    # Ignore response.
    ostream.close()

def get_next_command(timeout):
    global pollobj
    command = "None"
    evts = pollobj.poll(timeout)
    if len(evts) > 0:
        (fd, event) = evts[0]
        if event == select.POLLIN:
            command = sys.stdin.readline()
            command = command[:-1]
    return command

############## Main

if len(sys.argv) != 2:
    raise RuntimeError("usage: photogen.py upload-url")

UPLOAD_URL = sys.argv[1]

state = 'WAIT'
pollobj = select.poll()
pollobj.register(sys.stdin, select.POLLIN)
# Initialize camera an http upload objects.
camera = picamera.PiCamera()
camera.vflip = True
camera.hflip = True
register_openers()
time.sleep(2) # Allow for camera warm-up

state = "WAITING"
while True:
    #print "State=" + state
    # Wait for a command:
    # Read stdin
    # Check what the command is. Currently only START and STOP are supported.
    # If state is 'CAPTURING', only STOP is recognized.
    # If state is 'WAITING', only START is recognized.
    # If comand is START, begin camera capture + upload
    if state == 'WAITING':
        command = get_next_command(None)
        if command == 'START':
            photo = capture_photo(camera)
            state = 'UPLOADING'
    elif state == 'UPLOADING':
        command = get_next_command(0)
        if command == 'STOP':
            # There's always a photo in the uploading state
            photo = add_text(photo)
            state = 'STOPPING'
        else:
            upload_photo(photo)
            state = 'CAPTURING'
    elif state == 'STOPPING':
        # Ignore all commands in the stopping state
        upload_photo(photo)
        state = 'WAITING'
    elif state == 'CAPTURING':
        command = get_next_command(0)
        if command == 'STOP':
            photo = capture_photo(camera)
            photo = add_text(photo)
            state = 'STOPPING'
        else:
            photo = capture_photo(camera)
            state = 'UPLOADING'

