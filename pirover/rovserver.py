#!/usr/bin/python

# This script runs inside the RPi and listens for rover commands.
# It also takes pictures and uploads to URL.

import RPi.GPIO as GPIO
import time
import atexit
import fileinput
import re
import SocketServer
import ConfigParser
import sys
import picamera
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers
import urllib2
import subprocess

# the poster package can be obtained from:
# http://atlee.ca/software/poster/dist/0.8.1

HOST = "0.0.0.0" # Change to localhost if not listening from outisde

def pulse(pin, duration, duty_cycle):
    """ Simulate PWM.

    pin: One of PIN_LEFT or PIN_RIGHT
    duraion: Total pulse time in seconds. Can be floating point.
    duty_cycle: Ratio of pulse_high to total cycle time. Must always be
    between 0 and 1.0 """

    endtime = time.time() + duration
    duration_on = duty_cycle * TC
    duration_off = TC - duration_on
    while endtime > time.time():
        GPIO.output(pin, True)
        time.sleep(duration_on)
        GPIO.output(pin, False)
        time.sleep(duration_off)

# pin_corr must be one of PIN_RIGHT or PIN_LEFT.
# See paramater for pulse() for definition of duty_cycle
def forward(duration, pin_corr=None, duty_cycle = 1):
    #print "Forward"
    if pin_corr and pin_corr != PIN_LEFT and pin_corr != PIN_RIGHT:
        raise RuntimeError("Invalid pin_corr")

    pin_const = PIN_RIGHT
    if pin_corr == PIN_RIGHT:
        pin_const = PIN_LEFT

    if pin_corr:
        GPIO.output(pin_const, True)
        starttime = time.time()
        endtime = starttime + duration
        pulse(pin_corr, duration, duty_cycle)
    else:
        GPIO.output(PIN_RIGHT, True)
        GPIO.output(PIN_LEFT, True)
        time.sleep(duration)


def stop():
    #print "Stop"
    GPIO.output(PIN_LEFT, False)
    GPIO.output(PIN_RIGHT, False)

def cleanup():
    print "Cleaning up"
    GPIO.output(PIN_LEFT, False)
    GPIO.output(PIN_RIGHT, False)
    GPIO.cleanup()

def left(duration, duty_cycle):
    print "Left turn for ", duration
    GPIO.output(PIN_RIGHT, True)
    pulse(PIN_LEFT, duration, duty_cycle)
    stop()

def right(duration, duty_cycle):
    print "Right turn for ", duration
    # Keep left track moving, slow down the right one.
    GPIO.output(PIN_LEFT, True)
    pulse(PIN_RIGHT, duration, duty_cycle)
    stop()

def process_cmd(cmd):
    print "Processing: ", cmd
    m = re.match('([lrfsLRFS])(\d+)', cmd)
    if not m:
        return
    command = m.group(1).lower()
    deltastr = m.group(2)
    delta = int(deltastr)
    if delta > 30 or delta < 0:
        return
    if command == "r":
        if delta > 5:
            delta = 5
        right(delta, RIGHT_TURN_DUTY_CYCLE)
    elif command == "l":
        if delta > 5:
            delta = 5
        left(delta, LEFT_TURN_DUTY_CYCLE)
    elif command == "s":
        stop() # This is really a NO-OP for now. Will be useful later.
    elif command == "f":
        forward(delta, pin_corr, FWD_CORRECTION_DUTY_CYCLE)

        stop()

def handle_request(lines):
    print "Command: ", lines
    lines = lines.lower()
    lines = lines.strip()
    cmds = lines.split()

    if len(cmds) > 10:
        return

    for cmd in cmds:
        process_cmd(cmd)

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        if len(data) <= 100:
            obj = subprocess.Popen(['./photogen.py'], stdin=subprocess.PIPE)
            handle_request(data)
            obj.communicate(input="STOP")

def process_photo(camera):
    print "Capturing image.."
    camera.capture('image.png', resize=(320, 240))
    camera.close()
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

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("syntax: pirover configfile")

    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])

    PIN_LEFT = config.getint('RPI', 'PIN_LEFT')
    PIN_RIGHT = config.getint('RPI', 'PIN_RIGHT')
    FWD_CORRECTION_PIN = config.get('CHASSIS', 'FWD_CORRECTION_PIN')
    FWD_CORRECTION_DUTY_CYCLE = config.getfloat('CHASSIS', 'FWD_CORRECTION_DUTY_CYCLE')
    LEFT_TURN_DUTY_CYCLE = config.getfloat('CHASSIS', 'LEFT_TURN_DUTY_CYCLE')
    RIGHT_TURN_DUTY_CYCLE = config.getfloat('CHASSIS', 'RIGHT_TURN_DUTY_CYCLE')
    PORT = config.getint('RPI', 'PORT')
    TC = config.getfloat('CHASSIS', 'TC')
    UPLOAD_URL = config.get('RPI', 'UPLOAD_URL')

    if FWD_CORRECTION_PIN == 'PIN_RIGHT':
        pin_corr = PIN_RIGHT
    elif FWD_CORRECTION_PIN == 'PIN_LEFT':
        pin_corr = PIN_LEFT
    elif FWD_CORRECTION_PIN == 'None':
        pin_corr = None
    else:
        raise RuntimeError("FWD_CORRECTION_PIN must be one of PINLEFT, PIN_RIGHT or None")


    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN_LEFT, GPIO.OUT)
    GPIO.setup(PIN_RIGHT, GPIO.OUT)
    # Register the streaming http handlers with urllib2
    register_openers()
    atexit.register(cleanup)

    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    server.serve_forever()
