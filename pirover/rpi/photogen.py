#!/usr/bin/python
from collections import deque
import sys, time, select
import FSM

# These are in seconds
WARM_WAIT_TIMEOUT = 100 # How many seconds we wait with camera activated
MAX_UPLOAD_PERIOD = 45 # Stop uploading after this seconds.

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
from collections import deque

def add_text(stream):
    #print "Adding text"
    global GUIDELINE_LL_X
    global GUIDELINE_LR_X
    global GUIDELINE_UL_X
    global GUIDELINE_UR_X
    global GUIDELINE_TOP
    global GUIDELINE_BOTTOM

    image = Image.open(stream)
    draw = ImageDraw.Draw(image)
    draw.line([(GUIDELINE_LL_X, GUIDELINE_BOTTOM),(GUIDELINE_UL_X, GUIDELINE_TOP)], width=2, fill=128)
    draw.line([(GUIDELINE_LR_X, GUIDELINE_BOTTOM),(GUIDELINE_UR_X, GUIDELINE_TOP)], width=2, fill=128)
    now = datetime.now()
    str = now.strftime("%H:%M")
    draw.text((0, 0), str)
    #PIL cannot save to a stream, so write to a file and read it back.
    image.save("tmp.jpg", format="jpeg")
    fp = open("tmp.jpg", "rb")
    stream.close()
    return fp

def capture_photo():
    #print "Capturing image.."
    global camera
    if not camera:
        camera_on()
    ostream = io.BytesIO()
    camera.capture(ostream, format='jpeg', resize=(320, 240),
                   use_video_port=True)
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

def camera_on():
    global camera
    camera = picamera.PiCamera()
    camera.vflip = True
    camera.hflip = True

def capture():
    #print "**************Capturing"
    global fsm
    global photo
    photo = capture_photo()
    # Reset timer(s)
    # Check if there's an event. If not, generate COMPLETE
    if fire_timed_events() == 0:
        if not wait_command(timeout=0):
            fsm.enqueue_event('COMPLETE')

def final_capture():
    global timers
    del timers['UPLOAD_TIMEOUT']
    return capture()

def upload():
    global fsm
    global photo
    #print "**************Uploading"
    upload_photo(photo)
    if fire_timed_events() == 0:
        if not wait_command(timeout=0):
            fsm.enqueue_event('COMPLETE')

def upload_text():
    global fsm
    global photo
    #print "************Adding text and uploading"
    photo = add_text(photo)
    upload_photo(photo)
    fsm.enqueue_event('COMPLETE')

def wait_command(timeout=None):
    # print "Waiting for a command.."
    global pollobj
    global fsm

    pollevts = pollobj.poll(timeout)
    if len(pollevts) > 0:
        pollfd, pollevt = pollevts[0]
        if pollevt == select.POLLIN:
            inline = sys.stdin.readline()
            event = inline[:-1] # Remove newline
            fsm.enqueue_event(event)
            if event == 'START':
               add_timed_event('UPLOAD_TIMEOUT',
                               time.time() + MAX_UPLOAD_PERIOD, 'PAUSE')
            return True
    return False

def wait_command_timeout():
    global fsm
    if not wait_command(timeout=WARM_WAIT_TIMEOUT * 1000):
        fsm.enqueue_event('COMPLETE')

def cold_wait_command():
    #print "***** Turning cam off"
    global camera
    camera.close()
    camera = None
    return wait_command()

def add_timed_event(name, endtime, event):
    global timers
    timers[name] = (endtime, event)

def fire_timed_events():
    nevents = 0
    global fsm
    global timers
    for k, v in timers.iteritems():
        if v:
            (endtime, event) = v
            if time.time() >= endtime:
               fsm.enqueue_event(event)
               nevents += 1
               timers[k] = None
    return nevents

############################## Begin main ##################################
if len(sys.argv) != 8:
    raise RuntimeError("usage: photogen.py upload-url LL_X LR_X UL_X UR_X TOP BOTTOM")
UPLOAD_URL = sys.argv[1]
GUIDELINE_LL_X = int(sys.argv[2])
GUIDELINE_LR_X = int(sys.argv[3])
GUIDELINE_UL_X = int(sys.argv[4])
GUIDELINE_UR_X = int(sys.argv[5])
GUIDELINE_TOP = int(sys.argv[6])
GUIDELINE_BOTTOM = int(sys.argv[7])

state_table = {}
state_table['INIT-BEGIN'] = ['WARM_WAIT', wait_command_timeout]
state_table['WARM_WAIT-START'] = ['CAPTURING', capture]
state_table['WARM_WAIT-PAUSE'] = ['WARM_WAIT', wait_command_timeout] # NO-OP
state_table['WARM_WAIT-COMPLETE'] = ['COLD_WAIT', cold_wait_command] # NO-OP
state_table['CAPTURING-COMPLETE'] = ['UPLOADING', upload]
state_table['CAPTURING-PAUSE'] = ['FINAL_UPLOAD', upload_text]
state_table['UPLOADING-COMPLETE'] = ['CAPTURING', capture]
state_table['UPLOADING-PAUSE'] = ['FINAL_CAPTURE', final_capture]
state_table['FINAL_CAPTURE-COMPLETE'] = ['FINAL_UPLOAD', upload_text]
state_table['FINAL_CAPTURE-PAUSE'] = ['FINAL_UPLOAD', upload_text]
state_table['FINAL_CAPTURE-START'] = ['FINAL_UPLOAD', upload_text]
state_table['FINAL_UPLOAD-COMPLETE'] = ['WARM_WAIT', wait_command_timeout]
state_table['COLD_WAIT-START'] = ['CAPTURING', capture]

fsm = FSM.FSM(state_table)
# The format is EVENT_NAME => (endtime, evenststr)
timers = {}

pollobj = select.poll()
pollobj.register(sys.stdin, select.POLLIN)
photo = None

register_openers()
camera_on()

fsm.enqueue_event('BEGIN')
fsm.run()
