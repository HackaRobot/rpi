#!/usr/bin/python


# The conections are as follows:
#=====================+========================+=============================+
#    L293D            |      RPi Pin#          | Comments                    |
#=====================+========================+=============================+
#  Pins 1,9 (En)      |      Pin 12 (GPIO 18)  |                             |
#---------------------+------------------------+-----------------------------+
#  Pin  15 (4A)       |      Pin 15 (GPIO 22)  |                             |
#---------------------+------------------------+-----------------------------+
#  Pin  8 (Vcc2)      |                        | Connect to +4.5 V   battery |
#---------------------+------------------------+-----------------------------+
# Also connect -ve of battery to ground (GND).

# servod starts up with following output:
# 
# Board revision:                  2
# Using hardware:                PWM
# Using DMA channel:              14
# Idle timeout:             Disabled
# Number of servos:                1
# Servo cycle time:            20000us
# Pulse increment step size:      10us
# Minimum width value:            50 (500us)
# Maximum width value:           170 (1700us)
# Output levels:              Normal
# 
# Using P1 pins:               15
# Using P5 pins:
# 
# Servo mapping:
# 

import RPi.GPIO as GPIO
import time
import atexit
import sys

def cleanup():
    print "Cleaning up"
    GPIO.output(12, False)
    GPIO.cleanup()

def position(angle):
    str = "0={0}\n".format(angle)
    print "Positioning to " + str,
    fd = open("/dev/servoblaster", "w")
    fd.write(str)
    fd.close()

def sweep():
    position(50)
    time.sleep(0.25)
    position(170)
    time.sleep(0.5)
    position(50)
    time.sleep(0.5)


GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT) #Enable

atexit.register(cleanup)
GPIO.output(12, True)

for i in range(5):
    sweep()

print "Done"
