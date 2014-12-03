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
import fileinput
import re


def cleanup():
    print "Cleaning up"
    GPIO.output(12, False)
    GPIO.cleanup()

def position(angle):
    str = "0={0}\n".format(angle)
    #print "Positioning to " + str,
    fd = open("/dev/servoblaster", "w")
    fd.write(str)
    fd.close()


GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT) #Enable

atexit.register(cleanup)
GPIO.output(12, True)

print "Start music in.."
for sec in range(5, 0, -1):
    print sec
    time.sleep(1)
print "NOW!"
starttime = time.time()

lineno = 1
prog = re.compile("(\d+)\s+([\d\.]+)")
for line in fileinput.input():
    result = prog.match(line)
    if (result and lineno > 0):
        angle = int(result.group(1)) * 120 / 500 + 50
        delta = float(result.group(2))
        position(angle)
        # delta is seconds from the begin of music
        nowtime = time.time()
        endtime = starttime + delta
        tosleep = endtime - nowtime
        #print "Sleep ", tosleep
        if tosleep > 0:
            time.sleep(tosleep)
    lineno += 1
        

