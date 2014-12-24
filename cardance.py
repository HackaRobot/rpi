#!/usr/bin/python

# This script makes a RC car "dance" using a raspberry pi. 
# Author: Sandeep Mukherjee
#
# You will need:
# An orinary RC car (I used a cheap $20 one from a local store).
# Functional Raspberry pi B or higher. Tested using raspbian 3.12.28,
#   although higher versions will probably work.
# L293D motor controller.
# Jumper cables.
# 4.5V battery supply. (9V might also work, but there's a risk of motor burnout)
# Breadboard for easy connections.

# Cut the drive motor and steering servo wires from the radio unit in the car.
# These will be connected to the L29D as described below.
# "Jack up" the RC car so that the rear wheels don't actually move the car.
# Power up the pi, then run this script as root.
# See http://youtu.be/IePczQQMoZQ for a demo. (corresponds to commit# 
#      ecb918a435a239fead08071f1d97c88ba4ac5110 )

# The conections are as follows:
#=====================+========================+=============================+
#    L293D            |      RPi Pin#          | Comments                    |
#=====================+========================+=============================+
#  Pins 1,9 (En)      |      Pin 12 (GPIO 18)  |                             |
#---------------------+------------------------+-----------------------------+
#  Pin 16 (Vcc1)      |      Pin 2 (5v)        |                             |
#---------------------+------------------------+-----------------------------+
#  Pin  4 (GND)       |      Pin 6 (GND)       | Connect to ground           |
#---------------------+------------------------+-----------------------------+
#  Pin  3 (1Y)        |                        | Connect to motor terminal 1 |
#---------------------+------------------------+-----------------------------+
#  Pin  6 (2Y)        |                        | Connect to motor terminal 2 |
#---------------------+------------------------+-----------------------------+
#  Pin  7 (2A)        |      Pin 11 (GPIO 17)  |                             |
#---------------------+------------------------+-----------------------------+
#  Pin  2 (1A)        |      Pin 13 (GPIO 21)  |                             |
#---------------------+------------------------+-----------------------------+
#  Pin  15 (4A)       |      Pin 15 (GPIO 22)  |                             |
#---------------------+------------------------+-----------------------------+
#  Pin  10 (3A)       |      Pin 16 (GPIO 23)  |                             |
#---------------------+------------------------+-----------------------------+
#  Pin  11 (3Y)       |                        | Steering servo wire 1       |
#---------------------+------------------------+-----------------------------+
#  Pin  14 (4Y)       |                        | Steering servo wire 2       |
#---------------------+------------------------+-----------------------------+
#  Pin  8 (Vcc2)      |                        | Connect to +4.5 V   battery |
#---------------------+------------------------+-----------------------------+
# Also connect -ve of battery to ground (GND).

import RPi.GPIO as GPIO
import time
import atexit

def left():
    print "Left turn"
    GPIO.output(15, True)
    GPIO.output(16, False)

def center():
    print "Straight"
    GPIO.output(15, False)
    GPIO.output(16, False)

def right():
    print "Right turn"
    GPIO.output(16, True)
    GPIO.output(15, False)

def forward():
    print "Forward"
    GPIO.output(13, False)
    GPIO.output(11, True)

def reverse():
    print "Reverse"
    GPIO.output(13, True)
    GPIO.output(11, False)

def stop():
    print "Stop"
    GPIO.output(13, False)
    GPIO.output(11, False)

def cleanup():
    print "Cleaning up"
    GPIO.output(12, False)
    GPIO.output(11, False)
    GPIO.output(13, False)
    GPIO.output(15, False)
    GPIO.output(16, False)
    GPIO.cleanup()

# Moves the wheels from one side to the next,
# pausing for interval seconds, for a total of reps cycles
def wheelswing(interval, reps):
    for i in range(reps):
        left()
        time.sleep(interval)

        right()
        time.sleep(interval)
    center()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT) #Enable
GPIO.setup(11, GPIO.OUT) # This
GPIO.setup(13, GPIO.OUT) # And this must complement
GPIO.setup(15, GPIO.OUT) # this
GPIO.setup(16, GPIO.OUT) # And this must complement

atexit.register(cleanup)
GPIO.output(12, True)

for i in range(3):

    forward()
    time.sleep(1)

    stop()
    time.sleep(0.25)

    wheelswing(0.25, 1)
    time.sleep(0.55)

    reverse()
    time.sleep(1)
    stop()
    time.sleep(0.25)
