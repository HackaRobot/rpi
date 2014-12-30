#! /usr/pkg/bin/python

import ConfigParser
import sys

if len(sys.argv) != 2:
    raise RuntimeError("syntax: pirover configfile")

def start_cam():
    pid = os.fork()
    if pid == 0:
        # This is the child process. Take pics and exit.
        atexit.register(None)
        endtime = time.time() + duration
        while time.time() < endtime:
            cmd = "fswebcam images/snapshot.jpg"
            print "Calling: " + cmd
            subprocess.call(cmd)
            time.sleep(1)
        exit(0)
    else:
        return pid
config = ConfigParser.RawConfigParser()
config.read(sys.argv[1])

PIN_LEFT = config.getint('RPI', 'PIN_LEFT')
PIN_RIGHT = config.getint('RPI', 'PIN_RIGHT')
FWD_CORRECTION_PIN = config.get('CHASSIS', 'FWD_CORRECTION_PIN')
FWD_CORRECTION_DUTY_CYCLE = config.getfloat('CHASSIS', 'FWD_CORRECTION_DUTY_CYCLE')
DUTY_PERIOD = config.getfloat('CHASSIS', 'DUTY_PERIOD')
LEFT_TURN_DUTY_CYCLE = config.getfloat('CHASSIS', 'LEFT_TURN_DUTY_CYCLE')
RIGHT_TURN_DUTY_CYCLE = config.getfloat('CHASSIS', 'RIGHT_TURN_DUTY_CYCLE')

print DUTY_PERIOD

start_cam()


