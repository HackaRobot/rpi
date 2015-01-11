#! /usr/pkg/bin/python

import cgi
import cgitb
import socket
import time

# Change these to match your configuration
# Host is the IP address of the RPi
# CUSTOMIZE: Replace with your RPI's IP address.
HOST, PORT = "your.rpi.ip.addr", 9999

refresh_max = 30 # How many seconds are you allowed to auto-refresh

def send_req(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
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
print                               # blank line, end of headers

print "<TITLE>Pi Rover Control</TITLE>"

print "<h1> Pi Rover Control</h1>"

form = cgi.FieldStorage()
if "click" not in form:
    print "<H1>Error</H1>"
    print "Invalid Input"
else:
    cmd = form["click"].value

    if cmd == "Right":
        cmdstr = "r"
    elif cmd == "Left":
        cmdstr = "l"
    elif cmd == "Forward":
        cmdstr = "f"
    elif cmd == "Stop":
        cmdstr = "s"

    duration = None
    if "duration" in form:
        duration = form["duration"].value
    if not duration:
        duration = "5"

    cmdstr = cmdstr + duration
    send_req(cmdstr)

    repeat_until = int(time.time()) + refresh_max
    str1 = """

<form method="post" action="click.cgi" enctype="multipart/form-data">
<p>

    Duration: 
    <input type="text"
        name="duration"
        value="{0}"
        size="10" maxlength="10" />
    <br>
    <input type="submit" name="click" value="Left"/>
    <input type="submit" name="click" value="Stop"/>
    <input type="submit" name="click" value="Forward"/>
    <input type="submit" name="click" value="Right"/>

</p>
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

print str1.format(duration)

print "</body></html>"
