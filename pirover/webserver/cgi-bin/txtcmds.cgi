#! /usr/pkg/bin/python

import cgi
import cgitb
import socket
import re
import time

SIM_MODE = False
# Host is the IP address of the RPi
# CUSTOMIZE: Replace with your RPI's IP address.
HOST, PORT = "your.rpi.ip.addr", 9999
refresh_max = 30 # How many seconds are you allowed to auto-refresh

def print_html(trimval):
    repeat_until = int(time.time()) + refresh_max
    str1 = """

<form method="post" action="click.cgi" enctype="multipart/form-data">
<p>

    Duration: 
    <input type="text"
        name="duration"
        value="5"
        size="10" maxlength="10" />
    <br>
    <input type="submit" name="click" value="Left"/>
    <input type="submit" name="click" value="Stop"/>
    <input type="submit" name="click" value="Forward"/>
    <input type="submit" name="click" value="Right"/>

</p>
    Trim: Left<input type="range" name="trim" value={0} min="-10" max="10"/>Right
</form>

<hr/>

<form method="post" action="txtcmds.cgi" enctype="multipart/form-data">

<p>
Enter commands: 
<br/>
    <textarea rows="4" cols="10" name="txtcmds" placeholder="Rover Commands"></textarea> 
(E.g. f10 r3 moves rover forward 10 seconds, then turns right for 3) <br/>
    <input type="submit" name="click" value="Go"/>
</p>
</form>
<img src="image.cgi"></img>
"""
    print str1.format(trimval)


def send_req(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(data, (HOST, PORT))

def process_text(text):
    # All commands must follow the correct syntax and there cannot be more than
    # 10 commands at a time.
    # Else discard the entire text
    tokens = text.split()
    if len(tokens) > 10:
        return
    for token in tokens:
        if not re.match('([lrfsLRFS])(\d+)', token):
            return

    send_req(text.lower())

cgitb.enable()
print "Content-Type: text/html"     # HTML is following
print """
<style>
  body {background-color:lightgrey}
  h1   {color:blue}
  p    { color:green; font-size:200% }
  input {font-face:'Comic Sans MS';
            font-size: larger;
            color: teal;
            background-color: #FFFFC0;
            border: 3pt ridge lightgrey;
        }
    textarea {
        font-size: larger
    }

</style>
"""
print                               # blank line, end of headers

print "<TITLE>Pi Rover Control</TITLE>"

print "<h1> Pi Rover Control</h1>"

form = cgi.FieldStorage()
if "click" not in form:
    print "<H1>Error</H1>"
    print "Invalid Input"
else:
    trimval = 0
    if "trim" in form:
        trimstr = form["trim"].value
        trimval = int(trimstr)
    alltext = form["txtcmds"].value
    if len(alltext) < 100:
        print "Processing: ", alltext
        process_text(alltext)
    else:
        print "Command too big. Not processing."

print_html(trimval)
print "</body></html>"
