#!/usr/bin/env python3

import http.server
import sys

def start_server(args, port=8798, bind="", cgi=False):
    if cgi==True:
        http.server.test(HandlerClass=http.server.CGIHTTPRequestHandler, port=port, bind=bind)
    else:
        http.server.test(HandlerClass=http.server.SimpleHTTPRequestHandler,port=port,bind=bind)

if __name__ == '__main__':
    sys.exit(start_server(sys.argv))
    