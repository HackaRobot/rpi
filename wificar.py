#!/usr/bin/python

# Python script to control a tracked vehicle like Tamiya crawler.
# This is work in progress.

import RPi.GPIO as GPIO
import time
import atexit
import fileinput
import re


PIN_LEFT = 23
PIN_RIGHT = 24

def forward(duration):
    print "Forward"
    GPIO.output(PIN_RIGHT, True)
    starttime = time.time()    
    endtime = starttime + duration
    while endtime > time.time():
        GPIO.output(PIN_LEFT, False)
        time.sleep(0.1)
        GPIO.output(PIN_LEFT, True)
        time.sleep(0.25)

def stop():
    print "Stop"
    GPIO.output(PIN_LEFT, False)
    GPIO.output(PIN_RIGHT, False)

def cleanup():
    print "Cleaning up"
    GPIO.output(PIN_LEFT, False)
    GPIO.output(PIN_RIGHT, False)
    GPIO.cleanup()

def left(duration):
    print "Left turn"
    GPIO.output(PIN_LEFT, True)
    # Keep right moving, but slowly
    starttime = time.time()    
    endtime = starttime + duration
    while endtime > time.time():
        GPIO.output(PIN_RIGHT, False)
        time.sleep(0.1)
        GPIO.output(PIN_RIGHT, True)
        time.sleep(0.1)

def right(duration):
    print "Right turn"
    GPIO.output(PIN_RIGHT, True)
    starttime = time.time()    
    endtime = starttime + duration
    while endtime > time.time():
        GPIO.output(PIN_LEFT, False)
        time.sleep(0.3)
        GPIO.output(PIN_LEFT, True)
        time.sleep(0.1)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_LEFT, GPIO.OUT)
GPIO.setup(PIN_RIGHT, GPIO.OUT)

atexit.register(cleanup)

for line in fileinput.input():
    m = re.match('([lrfs])\s+(\d+)', line)
    if m:
        command = m.group(1)
        delta = int(m.group(2))
        if command == "r":
            right(delta)
        elif command == "l":
            left(delta)
        elif command == "s":
            stop()
            time.sleep(delta)
        elif command == "f":
            forward(delta)

