#!/usr/bin/python
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

def enqueue_event(event):
    #print "Enqueueing: " + event
    events.append(event)

def have_events():
    return (len(events) > 0)


def deliver_event(event):
    global state
    str = state + '-' + event
    if not str in fsm:
        raise RuntimeError("Don't know how to handle event {0} while in state {1}".format(event, state))
    (nextstate, action) = fsm[str]
    print "Current state: {0}, event: {1}, next state: {2}".format(state, event, nextstate)
    state = nextstate;
    if action:
        action()

def fire_timed_events():
    global timers
    nevents = 0
    if 'PAUSE' in timers and (time.time() >= timers['PAUSE']):
       enqueue_event('PAUSE')
       nevents += 1
       del timers['PAUSE']
    return nevents

def capture(warmup = False):
    print "**************Capturing"
    global camera
    global photo

    if camera == None:
        camera = picamera.PiCamera()
        camera.vflip = True
        camera.hflip = True
        time.sleep(3)
    ostream = io.BytesIO()
    camera.capture(ostream, format='jpeg', resize=(320, 240), use_video_port=True)
    ostream.seek(0)
    photo = ostream

    # Check if there's an event. If not, generate COMPLETE
    if fire_timed_events() == 0:
        if not wait_command(timeout=0):
            enqueue_event('COMPLETE')

def capture_warmup():
    return capture(warmup=True)

def upload():
    print "**************Uploading"
    global photo
    upload_photo(photo)
    if fire_timed_events() == 0:
        if not wait_command(timeout=0):
            enqueue_event('COMPLETE')

def upload_text():
    print "************Adding text and uploading"
    global photo
    photo = add_text(photo)
    upload_photo(photo)
    enqueue_event('COMPLETE')

def get_next_event():
    if len(events) == 0:
        raise RuntimeError("Event queue is empty!")
    return events.popleft()

def wait_command(timeout=None):
    print "Waiting for a command.."
    global pollobj
    print "Wait for: ", timeout
    pollevts = pollobj.poll(timeout)
    print "Got something. sizeo evets=",len(pollevts)
    if len(pollevts) > 0:
        pollfd, pollevt = pollevts[0]
        if pollevt == select.POLLIN:
            inline = sys.stdin.readline()
            event = inline[:-1] # Remove newline
            enqueue_event(event)
            if event == 'START':
                timers['PAUSE'] = time.time() + 15
            return True
    return False

def wait_command_timeout():
    if not wait_command(timeout=15000):
        enqueue_event('COMPLETE')

def cold_wait_command():
    print "***** Turning cam off"
    global camera
    camera.close()
    camera = None
    return wait_command()

def begin_capture():
    timers['PAUSE'] = time.time() + 10
    return capture()

fsm = {}
fsm['INIT-BEGIN'] = ['WARM_WAIT', wait_command_timeout]
fsm['WARM_WAIT-START'] = ['CAPTURING', begin_capture]
fsm['WARM_WAIT-PAUSE'] = ['WARM_WAIT', wait_command_timeout] # NO-OP
fsm['WARM_WAIT-COMPLETE'] = ['COLD_WAIT', cold_wait_command] # NO-OP
fsm['CAPTURING-COMPLETE'] = ['UPLOADING', upload]
fsm['CAPTURING-PAUSE'] = ['FINAL_UPLOAD', upload_text]
fsm['UPLOADING-COMPLETE'] = ['CAPTURING', capture]
fsm['UPLOADING-PAUSE'] = ['FINAL_CAPTURE', capture]
fsm['FINAL_CAPTURE-COMPLETE'] = ['FINAL_UPLOAD', upload_text]
fsm['FINAL_UPLOAD-COMPLETE'] = ['WARM_WAIT', wait_command_timeout]
fsm['COLD_WAIT-START'] = ['CAPTURING', capture_warmup]
events = deque()
state = 'INIT'
timers = {}


if len(sys.argv) != 2:
    raise RuntimeError("usage: photogen.py upload-url")
UPLOAD_URL = sys.argv[1]
# Initialize camera an http upload objects.
camera = picamera.PiCamera()
camera.vflip = True
camera.hflip = True
register_openers()
time.sleep(2) # Allow for camera warm-up

pollobj = select.poll()
pollobj.register(sys.stdin, select.POLLIN)

enqueue_event('BEGIN')
while True:
    event = get_next_event()
    deliver_event(event)
