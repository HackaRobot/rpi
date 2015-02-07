#!/usr/bin/env python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import CGIHTTPServer
import threading

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 8000), CGIHTTPServer.CGIHTTPRequestHandler)
    print 'Starting server'
    server.serve_forever()

