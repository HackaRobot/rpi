#!/usr/bin/python

# Manually test tracked motor 

import RPi.GPIO as GPIO
import time
import atexit

PIN_LEFT_FWD = 11
PIN_LEFT_REV = 12
PIN_RIGHT_FWD = 22
PIN_RIGHT_REV = 21
PIN_ENABLE = 26

def right():
    print "Left turn"
    GPIO.output(PIN_RIGHT_FWD, False)
    GPIO.output(PIN_RIGHT_REV, True)
    GPIO.output(PIN_LEFT_FWD, True)
    GPIO.output(PIN_LEFT_REV, False)

def forward():
    print "Forward"
    GPIO.output(PIN_LEFT_FWD, True)
    GPIO.output(PIN_LEFT_REV, False)
    GPIO.output(PIN_RIGHT_FWD, True)
    GPIO.output(PIN_RIGHT_REV, False)

def left():
    print "Right turn"
    GPIO.output(PIN_RIGHT_FWD, True)
    GPIO.output(PIN_RIGHT_REV, False)
    GPIO.output(PIN_LEFT_FWD, False)
    GPIO.output(PIN_LEFT_REV, True)

def reverse():
    print "Reverse"
    GPIO.output(PIN_LEFT_FWD, False)
    GPIO.output(PIN_LEFT_REV, True)
    GPIO.output(PIN_RIGHT_FWD, False)
    GPIO.output(PIN_RIGHT_REV, True)

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

GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_LEFT_FWD, GPIO.OUT)
GPIO.setup(PIN_LEFT_REV, GPIO.OUT)
GPIO.setup(PIN_RIGHT_FWD, GPIO.OUT)
GPIO.setup(PIN_RIGHT_REV, GPIO.OUT)
GPIO.setup(PIN_ENABLE, GPIO.OUT)

atexit.register(cleanup)

enable()

forward()
time.sleep(5)

right()
time.sleep(2)

stop()
