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

    print "Pulsing pin {0} for {1} seconds with DC={2}".format(pin, duration, duty_cycle)
    endtime = time.time() + duration
    duration_on = duty_cycle * TC
    duration_off = TC - duration_on

    freq = 10
    p = GPIO.PWM(pin, freq)
    p.start(duty_cycle * 100)
    time.sleep(duration)
    p.stop()

def right(duration):
    print "Left turn"
    GPIO.output(PIN_RIGHT_FWD, False)
    GPIO.output(PIN_RIGHT_REV, True)
    GPIO.output(PIN_LEFT_FWD, True)
    GPIO.output(PIN_LEFT_REV, False)
    time.sleep(duration)

def forward(duration):
    print "Forward"
    GPIO.output(PIN_LEFT_FWD, True)
    GPIO.output(PIN_LEFT_REV, False)
    GPIO.output(PIN_RIGHT_FWD, True)
    GPIO.output(PIN_RIGHT_REV, False)
    time.sleep(duration)

def left(duration):
    print "Right turn"
    GPIO.output(PIN_RIGHT_FWD, True)
    GPIO.output(PIN_RIGHT_REV, False)
    GPIO.output(PIN_LEFT_FWD, False)
    GPIO.output(PIN_LEFT_REV, True)
    time.sleep(duration)

def reverse(duration):
    print "Reverse"
    GPIO.output(PIN_LEFT_FWD, False)
    GPIO.output(PIN_LEFT_REV, True)
    GPIO.output(PIN_RIGHT_FWD, False)
    GPIO.output(PIN_RIGHT_REV, True)
    time.sleep(duration)

def stop():
    print "Stop"
    GPIO.output(PIN_LEFT_FWD, False)
    GPIO.output(PIN_LEFT_REV, False)
    GPIO.output(PIN_RIGHT_FWD, False)
    GPIO.output(PIN_RIGHT_REV, False)

def enable():
    GPIO.output(PIN_ENABLE, True)

def disable():
    GPIO.output(PIN_ENABLE, False)

def cleanup():
    print "Cleaning up"
    GPIO.cleanup()

def process_cmd(cmd):
    global pin_corr
    global FWD_CORRECTION_DUTY_CYCLE

    print "Processing: ", cmd
    m = re.match('([lrfsLRFStTbB])(-*\d+)', cmd)
    if not m:
        return
    command = m.group(1).lower()
    deltastr = m.group(2)
    delta = int(deltastr)

    if command == 't':
        if delta < -10 or delta > 10:
            return
    else:
        if delta > 30 or delta <= 0:
            return
    if command == "r":
        if delta > 5:
            delta = 5
        right(delta)
    elif command == "l":
        if delta > 5:
            delta = 5
        left(delta)
    elif command == "s":
        time.sleep(delta)
    elif command == "f":
        forward(delta)
    elif command == "b":
        reverse(delta)

    stop()

def handle_request(lines):
    print "Command: ", lines
    lines = lines.lower()
    lines = lines.strip()
    cmds = lines.split()

    if len(cmds) > 10:
        return

    print "Sending command to photogen: START"
    photogen_handle.stdin.write("START\n")
    for cmd in cmds:
        process_cmd(cmd)
    print "Sending command to photogen: PAUSE"
    photogen_handle.stdin.write("PAUSE\n")

class MyUDPHandler(SocketServer.BaseRequestHandler):
    """
    This class works similar to the TCP handler class, except that
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """

    def handle(self):
        data = self.request[0].strip()
        global UPLOAD_URL
        if len(data) <= 100:
            handle_request(data)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise RuntimeError("syntax: pirover configfile")

    config = ConfigParser.RawConfigParser()
    config.read(sys.argv[1])

    PIN_LEFT_FWD = config.getint('RPI', 'PIN_LEFT_FWD')
    PIN_RIGHT_FWD = config.getint('RPI', 'PIN_RIGHT_FWD')
    PIN_LEFT_REV = config.getint('RPI', 'PIN_LEFT_REV')
    PIN_RIGHT_REV = config.getint('RPI', 'PIN_RIGHT_REV')
    PIN_ENABLE = config.getint('RPI', 'PIN_ENABLE')
    FWD_CORRECTION_PIN = config.get('CHASSIS', 'FWD_CORRECTION_PIN')
    FWD_CORRECTION_DUTY_CYCLE = config.getfloat('CHASSIS', 'FWD_CORRECTION_DUTY_CYCLE')
    LEFT_TURN_DUTY_CYCLE = config.getfloat('CHASSIS', 'LEFT_TURN_DUTY_CYCLE')
    RIGHT_TURN_DUTY_CYCLE = config.getfloat('CHASSIS', 'RIGHT_TURN_DUTY_CYCLE')
    PORT = config.getint('RPI', 'PORT')
    TC = config.getfloat('CHASSIS', 'TC')
    UPLOAD_URL = config.get('RPI', 'UPLOAD_URL')

    if FWD_CORRECTION_PIN == 'PIN_RIGHT':
        pin_corr = 0 # FIXME
    elif FWD_CORRECTION_PIN == 'PIN_LEFT':
        pin_corr = 0 # FIXME
    elif FWD_CORRECTION_PIN == 'None':
        pin_corr = None
    else:
        raise RuntimeError("FWD_CORRECTION_PIN must be one of PINLEFT, PIN_RIGHT or None")


    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(PIN_LEFT_FWD, GPIO.OUT)
    GPIO.setup(PIN_LEFT_REV, GPIO.OUT)
    GPIO.setup(PIN_RIGHT_FWD, GPIO.OUT)
    GPIO.setup(PIN_RIGHT_REV, GPIO.OUT)
    GPIO.setup(PIN_ENABLE, GPIO.OUT)
    # Register the streaming http handlers with urllib2
    register_openers()
    atexit.register(cleanup)
    enable()

    server = SocketServer.UDPServer((HOST, PORT), MyUDPHandler)
    photogen_handle = subprocess.Popen(['./photogen.py', UPLOAD_URL], stdin=subprocess.PIPE)
    server.serve_forever()
