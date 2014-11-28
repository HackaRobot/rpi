#!/usr/bin/python

# Motor Controller              |                   RPi Pin#  |
#===============================+=============================+

import RPi.GPIO as GPIO
import time
import random
import atexit
import sys

def forward():
    GPIO.output(19, False)
    GPIO.output(11, True)

def backward():
    GPIO.output(19, True)
    GPIO.output(11, False)

def stop():
    GPIO.output(19, False)
    GPIO.output(11, False)

def cleanup():
    print "Cleaning up"
    GPIO.output(12, False)
    GPIO.output(11, False)
    GPIO.output(19, False)
    GPIO.cleanup()

# Values of 0.05, 0.2 work nicely
def oscillate(runtime, stoptime):
    while True:
        forward()
        time.sleep(runtime)
        stop()
        time.sleep(stoptime)
        backward()
        time.sleep(runtime)
        stop()
        time.sleep(stoptime)
def staccato():
    while True:
        forward()
        time.sleep(0.05)
        stop()
        time.sleep(0.2)

if len(sys.argv) != 2:
    raise RuntimeError("usage: {0} oscillate | staccato".format(sys.argv[0]))
pattern = sys.argv[1]
print pattern
if (pattern != "oscillate") and (pattern != "staccato"):
    raise RuntimeError("Argument must be one of oscillate or staccato")

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT) #Enable
GPIO.setup(11, GPIO.OUT) # This
GPIO.setup(19, GPIO.OUT) # And this must complement

atexit.register(cleanup)

GPIO.output(12, True)

if pattern == "oscillate":
    oscillate(0.05, 0.5)
else:
    staccato()
        
GPIO.output(12, False)
GPIO.output(11, False)
GPIO.output(19, False)
GPIO.cleanup()
