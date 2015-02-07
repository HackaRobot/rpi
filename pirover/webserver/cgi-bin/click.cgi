#! /usr/bin/env python

import cgi
import cgitb
import socket
import time
import re
import utils

# Change these to match your configuration
# Host is the IP address of the RPi
# CUSTOMIZE: Replace with your RPI's IP address.
PORT = 9999

refresh_max = 30 # How many seconds are you allowed to auto-refresh

def send_req(data, ipaddr):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print "Sending request:" + data + " to " + ipaddr
    sock.sendto(data, (ipaddr, PORT))

def process_text_commands(text, ipaddr):
    # All commands must follow the correct syntax and there cannot be more than
    # 10 commands at a time.
    # Else discard the entire text
    tokens = text.split()
    if len(tokens) > 10:
        return
    for token in tokens:
        if not re.match('([lrfsLRFStTbB])(-*\d+)', token):
            return

    send_req(text.lower(), ipaddr)

cgitb.enable()
#print "Content-Type: text/html"     # HTML is following
#print

trimval = 0
duration = 5
ipaddr="Unknown"

form = cgi.FieldStorage()
if "ipaddr" not in form:
    print "<H1>Error</H1>"
    print "Invalid Input"
else:
    ipaddr = form["ipaddr"].value # Validate IP address. TODO
    cmdstr = ""
    if "trim" in form:
        trimstr = form["trim"].value
        trimval = int(trimstr)
        if trimval >= -10 and trimval <= 10:
            cmdstr = "T" + trimstr
    if "click" in form:
        cmd = form["click"].value
        if cmd == "Go":
            process_text_commands(form["txtcmds"].value, ipaddr)
        else:
            if "duration" in form:
                duration = form["duration"].value
            if not duration:
                duration = "5"
            if cmd == "Right":
                cmdstr = cmdstr + " r" + duration
            elif cmd == "Left":
                cmdstr = cmdstr + " l" + duration
            elif cmd == "Forward":
                cmdstr = cmdstr + " f" + duration
            elif cmd == "Snap":
                cmdstr = cmdstr + " s" + duration
            elif cmd == "Back":
                cmdstr = cmdstr + " b" + duration

            send_req(cmdstr, ipaddr)

utils.print_html_header()
utils.print_html_form(trimval=trimval, duration=duration, ipaddr=ipaddr)

