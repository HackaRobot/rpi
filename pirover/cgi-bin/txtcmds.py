#! /usr/pkg/bin/python

import cgi
import cgitb
import socket
import re

SIM_MODE = False
# Host is the IP address of the RPi
HOST, PORT = "99.121.26.127", 9999

def print_html():
    str1 = """

<form method="post" action="click.py" enctype="multipart/form-data">
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
</form>

<hr/>

<form method="post" action="txtcmds.py" enctype="multipart/form-data">

<p>
Enter commands: 
<br/>
    <textarea rows="4" cols="10" name="txtcmds" placeholder="Rover Commands"></textarea> 
(E.g. f10 r3 moves rover forward 10 seconds, then turns right for 3) <br/>
    <input type="submit" name="click" value="Go"/>
</p>
</form>
"""
    print str1


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
    alltext = form["txtcmds"].value
    if len(alltext) < 100:
        print "Processing: ", alltext
        process_text(alltext)
    else:
        print "Command too big. Not processing."

print_html()
print "</body></html>"
