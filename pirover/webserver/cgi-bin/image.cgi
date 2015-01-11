#!/usr/pkg/bin/python

import cgi
import cgitb
import pymjpeg
import sys
import time
from glob import glob

def send_header(key, value):
    print key + ': ',
    print value

def end_headers():
    print

def send_response(code):
    print "HTTP/1.0 {0} OK\r\n".format(code),

#send_response(200)
# Response headers (multipart)
for k, v in pymjpeg.request_headers().items():
    send_header(k, v)

# Multipart content
endtime = time.time() + 60
filename = "image.jpg"
while time.time() < endtime:
    # Part boundary string
    end_headers()
    print(pymjpeg.boundary)
    end_headers()
    # Part headers
    for k, v in pymjpeg.image_headers(filename).items():
        send_header(k, v)
    end_headers()
    # Part binary
    for chunk in pymjpeg.image(filename):
            sys.stdout.write(chunk)
    time.sleep(1)
