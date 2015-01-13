#! /usr/pkg/bin/python

import cgi
import cgitb
import socket
import time
import re

# Change these to match your configuration
# Host is the IP address of the RPi
# CUSTOMIZE: Replace with your RPI's IP address.
HOST, PORT = "your.rpi.ip.addr", 9999

refresh_max = 30 # How many seconds are you allowed to auto-refresh

def send_req(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    print "Sending request:" + data
    sock.sendto(data, (HOST, PORT))

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
def print_html_form(trimval=0, duration=5):
    html = """
<form method="post" action="click.cgi" enctype="multipart/form-data">
    <p>
        Trim: Left<input type="range" name="trim" value="{0}" min="-10" max="10"/>Right<br/>
        <textarea rows="4" cols="10" name="txtcmds" placeholder="Rover Commands"></textarea> </br>
        <input type="submit" name="click" value="Go"/>
    </p>
    <p>
        Enter commands above or click buttons below: <br/>
        Duration: 
        <input type="text"
            name="duration"
            value="{1}"
            size="10" maxlength="10" />
    <br/>
    <input type="submit" name="click" value="Left"/>
    <input type="submit" name="click" value="Forward"/>
    <input type="submit" name="click" value="Right"/>
    <br/>
</p>
    <input type="submit" name="click" value="Snap"/>
</form>

<img src="image.cgi"></img>
"""
    print html.format(trimval, duration)

def process_text_commands(text):
    # All commands must follow the correct syntax and there cannot be more than
    # 10 commands at a time.
    # Else discard the entire text
    tokens = text.split()
    if len(tokens) > 10:
        return
    for token in tokens:
        if not re.match('([lrfsLRFStT])(-*\d+)', token):
            return

    send_req(text.lower())


print                               # blank line, end of headers

print "<TITLE>Pi Rover Control</TITLE>"

print "<h1> Pi Rover Control</h1>"

trimval = 0
duration = 5

form = cgi.FieldStorage()
if "click" not in form:
    print "<H1>Error</H1>"
    print "Invalid Input"
else:
    cmdstr = ""
    if "trim" in form:
        trimstr = form["trim"].value
        trimval = int(trimstr)
        if trimval >= -10 and trimval <= 10:
            cmdstr = "T" + trimstr
    cmd = form["click"].value
    if cmd == "Go":
        process_text_commands(form["txtcmds"].value)
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

        send_req(cmdstr)

print_html_form(trimval=trimval, duration=duration)

print "</body></html>"
