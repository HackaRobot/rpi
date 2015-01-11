#! /usr/pkg/bin/python
# This CGI script receives an image file and saves it as image.png

import cgi
import cgitb
import socket
import os

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
    fp = open("image.jpg.tmp", "w")
    fp.write(image)
    fp.close()
    os.rename("image.jpg.tmp", "image.jpg")
    print "Image saved. Length="
    print len(image)


print "</body></html>"