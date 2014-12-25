#!/usr/bin/python

# Python script to control a tracked vehicle like Tamiya crawler.
# This is work in progress.

import RPi.GPIO as GPIO
import time
import atexit
import fileinput
import re


PIN_LEFT = 24 # Turn this on to move the left track.
PIN_RIGHT = 23 # Turn this on to move the right track.

def pulse(pin, duration_on, duration_off, endtime):
    while endtime > time.time():
        GPIO.output(pin, False)
        time.sleep(duration_off)
        GPIO.output(pin, True)
        time.sleep(duration_on)

# pin_corr must be one of PIN_RIGHT or PIN_LEFT.
# If rover deviates to right, use PIN_LEFT
# Otherwise use PIN_RIGHT.
# corr_on is duration of time pin_corr remains on.
# corr_off is the duration it remains off.
# Smaller corr_on results in larger correction.
def forward(duration, pin_corr, corr_on):
    print "Forward"
    if pin_corr != PIN_LEFT and pin_corr != PIN_RIGHT:
        raise RuntimeError("Invalid pin_corr")
    
    pin_const = PIN_RIGHT
    if pin_corr == PIN_RIGHT:
        pin_const = PIN_LEFT

    GPIO.output(pin_const, True)
    starttime = time.time()    
    endtime = starttime + duration

    if corr_on < 0 or corr_on > 1.0:
        raise RuntimeError("corr_on must be between 0 and 1.0")
    corr_off = 1.0 - corr_on
    pulse(pin_corr, corr_on, corr_off, endtime)


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
    # Keep the right belt moving, and slow down the left one.
    GPIO.output(PIN_RIGHT, True)
    starttime = time.time()    
    endtime = starttime + duration
    while endtime > time.time():
        GPIO.output(PIN_LEFT, False)
        time.sleep(0.2)
        GPIO.output(PIN_LEFT, True)
        time.sleep(0.1)

def right(duration):
    print "Right turn"
    # Keep left belt moving, slow down the right one.
    GPIO.output(PIN_LEFT, True)
    starttime = time.time()    
    endtime = starttime + duration
    while endtime > time.time():
        GPIO.output(PIN_RIGHT, False)
        time.sleep(0.3)
        GPIO.output(PIN_RIGHT, True)
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
            forward(delta, PIN_LEFT, 0.85)

