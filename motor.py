#!/usr/bin/python

# This script controls a simple motor connected to a Rapberry Pi via a
# L293D motor controller.
# The conections are as follows:

#    L293D            |      RPi Pin#          | Comments
#=====================+========================+=============================+
#  Pin 1 (En)         |      Pin 12 (GPIO 18)  |                             |
#---------------------+------------------------+-----------------------------+
#  Pin 16 (Vcc1)      |      Pin 2 (5v)        |                             |
#---------------------+------------------------+-----------------------------+
#  Pin  4 (GND)       +      Pin 6 (GND)       + Connect to ground           |
#---------------------+------------------------+-----------------------------+
#  Pin  3 (1Y)        +                        + Connect to motor terminal 1 |
#---------------------+------------------------+-----------------------------+
#  Pin  6 (2Y)        +                        + Connect to motor terminal 2 |
#---------------------+------------------------+-----------------------------+
#  Pin  7 (2Y)        +      Pin 11 (GPIO 17)  +                             |
#---------------------+------------------------+-----------------------------+
#  Pin  2 (2Y)        +      Pin 13 (GPIO 21)  +                             |
#---------------------+------------------------+-----------------------------+
#  Pin  8 (Vcc2)      +                        +Connect to +9 V from battery |
#---------------------+------------------------+-----------------------------+
# Also connect -ve of battery to ground (GND).
# See http://youtu.be/Q7DNpWvGw90 and
# http://youtu.be/mbdJMM7fMu0 for demo.

import RPi.GPIO as GPIO
import time
import random
import atexit
import sys

def forward():
    GPIO.output(13, False)
    GPIO.output(11, True)

def backward():
    GPIO.output(13, True)
    GPIO.output(11, False)

def stop():
    GPIO.output(13, False)
    GPIO.output(11, False)

def cleanup():
    print "Cleaning up"
    GPIO.output(12, False)
    GPIO.output(11, False)
    GPIO.output(13, False)
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
GPIO.setup(13, GPIO.OUT) # And this must complement

atexit.register(cleanup)

GPIO.output(12, True)

if pattern == "oscillate":
    oscillate(0.05, 0.5)
else:
    staccato()
        
GPIO.output(12, False)
GPIO.output(11, False)
GPIO.output(13, False)
GPIO.cleanup()
