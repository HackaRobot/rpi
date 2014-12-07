#!/usr/bin/python


# The conections are as follows:
#=====================+========================+=============================+
#    L293D            |      RPi Pin#          | Comments                    |
#=====================+========================+=============================+
#  Pin 9 (En)         |      Pin 11 (GPIO 17)  |  Used to enable L293D       |
#---------------------+------------------------+-----------------------------+
#  Pin  15 (4A)       |      Pin 15 (GPIO 22)  |Controlled by servoblaster   |
#---------------------+------------------------+-----------------------------+
#  Pin  16 (Vcc1)     |      Pin 2             | 5V Power                    |
#---------------------+------------------------+-----------------------------+
#  Pin  8 (Vcc2)      |                        | Connect to +4.5 V   battery |
#---------------------+------------------------+-----------------------------+
#  Pin 13 (GND)       |     Pin 3              | Connect to Ground (GND)     |
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
import re
import pygame.mixer

fd = None
PIN_ENABLE = 11 # GPIO pin to enable the motor driver
PIN_CLK    = 15 # Must be same as "Using P1 pins" line above

def cleanup():
    print "Cleaning up"
    pygame.mixer.music.stop()
    GPIO.output(PIN_ENABLE, False)
    GPIO.cleanup()

def position(angle):
    str = "0={0}\n".format(angle)
    #print "Positioning to " + str,
    fd.write(str)
    fd.flush()

if len(sys.argv) != 3:
    raise RuntimeError("usage: {0} musicfile servofile".format(sys.argv[0]))

musicfile = sys.argv[1]
servofile = sys.argv[2]
sfd = open(servofile, "r")



pygame.mixer.init(channels=2,frequency=48000,size=-16)
pygame.mixer.music.load(musicfile)

fd = open("/dev/servoblaster", "w")
GPIO.setmode(GPIO.BOARD)
GPIO.setup(PIN_ENABLE, GPIO.OUT) #Enable

atexit.register(cleanup)
GPIO.output(PIN_ENABLE, True)

pygame.mixer.music.play(0)
starttime = time.time()

prog = re.compile("(\d+)\s+([\d\.]+)")

for line in sfd:
    result = prog.match(line)
    if result:
        angle = int(result.group(1)) * 120 / 500 + 50 # The numbers depend on the servo being used
        delta = float(result.group(2))
        position(angle)
        # delta is seconds from the begin of music
        nowtime = time.time()
        endtime = starttime + delta
        tosleep = endtime - nowtime
        #print "Sleep ", tosleep
        if tosleep > 0:
            time.sleep(tosleep)
        
sfd.close()
fd.close()
