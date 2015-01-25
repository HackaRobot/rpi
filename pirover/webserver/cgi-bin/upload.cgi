#! /usr/pkg/bin/python
# This CGI script receives an image file and saves it as image.png

import cgi
import cgitb
import socket
import os
import time
import shutil

#If this is true, a folder called "archive" must exist. All images will
# get timestamped and stored
ARCHIVE_IMAGES = True

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
if "image" not in form:
    print "<H1>Error</H1>"
    print "Invalid Input"
else:
    image = form["image"].value
    tmpfile = "image.jpg.tmp"
    fp = open(tmpfile, "wb")
    fp.write(image)
    fp.close()
    shutil.move(tmpfile, "image.jpg")

    if ARCHIVE_IMAGES:
        archfile = "archive/{0}.jpg".format(time.time())
        fp2 = open(archfile, "wb")
        fp2.write(image)
        fp2.close()

    print "Image saved. Length="
    print len(image)


print "</body></html>"
