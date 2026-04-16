#!/usr/bin/env python3
"""Serve this lab from browser-labs/ so ../config.json is reachable.

Run: python serve.py
"""
import http.server
import os
import socketserver

PORT = 9090
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(HERE))

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("", PORT), http.server.SimpleHTTPRequestHandler) as httpd:
    print(f"Open http://localhost:{PORT}/{os.path.basename(HERE)}/")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
