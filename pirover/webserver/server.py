#!/usr/bin/python

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
from SocketServer import ThreadingMixIn
import CGIHTTPServer
import threading

class Handler(CGIHTTPServer.CGIHTTPRequestHandler):

    """
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        message =  threading.currentThread().getName()
        self.wfile.write(message)
        self.wfile.write('\n')
        return
    """

class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

if __name__ == '__main__':
    server = ThreadedHTTPServer(('0.0.0.0', 8000), CGIHTTPServer.CGIHTTPRequestHandler)
    print 'Starting server'
    server.serve_forever()

