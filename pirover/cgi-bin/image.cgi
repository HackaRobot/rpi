#! /usr/pkg/bin/python

import cgi
import cgitb
import time

duration = 5

cgitb.enable()
print "Content-Type: text/html"
form = cgi.FieldStorage()
metastr = ""
if "repeat_until" in form:
    rus = form["repeat_until"].value
    repeat_until = int(rus)
    if time.time() < repeat_until:
        metastr = "<meta http-equiv=\"refresh\" content=\"{0}\">".format(duration)
str = """
<html> 
	<head>
	{0}
	</head>
	<body>
		<img src="../image.png"></img>
	</body>
</html>

"""

print str.format(metastr)
