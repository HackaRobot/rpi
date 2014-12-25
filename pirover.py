#!/usr/bin/python

# Python script to control a tracked vehicle like Tamiya crawler from
# a raspberry pi
# See: http://youtu.be/XaVNxZlOPxU for a demo.
# You may have to change the values of PIN_LEFT and PIN_RIGHT below.
# The script takes the name of a file as argument. An example is:
# l 5     (Turn left for 5 seconds)
# f 20    (Move forward for 20 seconds)
# s 3     (Stop for 3 seconds)
# r 6     (Turn right for 6 seconds)

import RPi.GPIO as GPIO
import time
import atexit
import fileinput
import re
import argparse


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
def forward(duration, pin_corr, corr_on, corr_off):
    print "Forward"
    if pin_corr and pin_corr != PIN_LEFT and pin_corr != PIN_RIGHT:
        raise RuntimeError("Invalid pin_corr")
    
    pin_const = PIN_RIGHT
    if pin_corr == PIN_RIGHT:
        pin_const = PIN_LEFT

    if pin_corr:
        GPIO.output(pin_const, True)
        starttime = time.time()    
        endtime = starttime + duration
        pulse(pin_corr, corr_on, corr_off, endtime)
    else:
        GPIO.output(PIN_RIGHT, True)
        GPIO.output(PIN_LEFT, True)
        time.sleep(duration)


def stop(duration):
    print "Stop"
    GPIO.output(PIN_LEFT, False)
    GPIO.output(PIN_RIGHT, False)
    time.sleep(duration)

def cleanup():
    print "Cleaning up"
    GPIO.output(PIN_LEFT, False)
    GPIO.output(PIN_RIGHT, False)
    GPIO.cleanup()

def left(duration):
    print "Left turn"
    # Keep the right track moving, and slow down the left one.
    GPIO.output(PIN_RIGHT, True)
    starttime = time.time()    
    endtime = starttime + duration
    while endtime > time.time():
        GPIO.output(PIN_LEFT, False)
        time.sleep(0.1)
        GPIO.output(PIN_LEFT, True)
        time.sleep(0.1)

def right(duration):
    print "Right turn"
    # Keep left track moving, slow down the right one.
    GPIO.output(PIN_LEFT, True)
    starttime = time.time()    
    endtime = starttime + duration
    while endtime > time.time():
        GPIO.output(PIN_RIGHT, False)
        time.sleep(0.1)
        GPIO.output(PIN_RIGHT, True)
        time.sleep(0.1)

def parse_cmdline():
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--correct-left', action="store", type=int,
                        help="Correct towards left (between 0 and 100)")
    parser.add_argument('-r', '--correct-right', action="store", type=int,
                        help="Correct towards right (between 0 and 100)")
    parser.add_argument("steer_file", help="File with directions")
    args = parser.parse_args()
    return args

########################## Begin main #################################
args = parse_cmdline()
infile = open(args.steer_file, "r")
if args.correct_left and args.correct_right:
    raise RuntimeError("Only one of correct left or right is allowed")

pin_corr = None
corr_on = 1
corr_off = 0

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_LEFT, GPIO.OUT)
GPIO.setup(PIN_RIGHT, GPIO.OUT)
atexit.register(cleanup)

# For larger correction, increase the corr_off value
if args.correct_left:
    pin_corr = PIN_LEFT
    if args.correct_left < 0 or args.correct_left > 100:
        raise RuntimeError("Correction value must be between 0 and 100")
    corr_off = 1.0 * args.correct_left/100
    corr_on = 1.0 * (100 - args.correct_left)/100

if args.correct_right:
    pin_corr = PIN_RIGHT
    if args.correct_right < 0 or args.correct_right > 100:
        raise RuntimeError("Correction value must be between 0 and 100")
    corr_off = 1.0 * args.correct_right/100
    corr_on = 1.0 * (100 - args.correct_right)/100

for line in infile:
    m = re.match('([lrfs])\s+(\d+)', line)
    if m:
        command = m.group(1)
        delta = int(m.group(2))
        if command == "r":
            right(delta)
        elif command == "l":
            left(delta)
        elif command == "s":
            stop(delta)
        elif command == "f":
            forward(delta, pin_corr, corr_on, corr_off)

infile.close()
