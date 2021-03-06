#!/usr/bin/env python
# coding: utf-8
# Copyright 2017 Abram Hindle & Adam Ford, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib


def help():
    print "httpclient.py [GET/POST] [URL]\n"


class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body


class HTTPClient(object):
    def connect(self, host, port):
        # From CMPUT 404 Lab 2
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((host, port))
        return sock

    def get_code(self, data):
        return None

    def get_headers(self, data):
        return None

    def get_body(self, data):
        return None

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
        (host, port, path) = split_url(url)
        sock = self.connect(host, port)

        # Request syntax/headers from CMPUT 404 course slides
        # Unicode conversion from https://docs.python.org/2/howto/unicode.html
        request = unicode(
            "GET %s HTTP/1.1\r\n"
            "Host: %s\r\n"
            "\r\n" % (path, host), 'utf-8')

        sock.sendall(request)

        response = self.recvall(sock)

        code = int(response.split(' ')[1])
        body = response.split("\r\n\r\n")[1]
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        (host, port, path) = split_url(url)
        request_body = urllib.urlencode(args) if args else ""

        encoded_request_body = unicode(request_body, 'utf-8')
        request_body_size = len(encoded_request_body)

        sock = self.connect(host, port)

        # Request syntax/headers from CMPUT 404 course slides
        # Unicode conversion from https://docs.python.org/2/howto/unicode.html
        request = unicode(
            "POST %s HTTP/1.1\r\n"
            "Host: %s\r\n"
            "Content-Type: application/x-www-form-urlencoded\r\n"
            "Content-Length: %d\r\n"
            "\r\n" % (path, host, request_body_size), 'utf-8') \
            + encoded_request_body

        sock.sendall(request)

        response = self.recvall(sock)

        code = int(response.split(' ')[1])
        body = response.split("\r\n\r\n")[1]
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST(url, args)
        else:
            return self.GET(url, args)


def split_url(url):
    """Returns a 3-tuple: (host, port, path)"""

    # From https://docs.python.org/2/library/re.html
    pattern = r'^http://(?P<host>[^/:\s]+)(?::(?P<port>\d+))?(?P<path>/.*)?$'
    match = re.match(pattern, url)

    if match is not None:
        return match.group("host"), int(match.group("port") or 80), match.group("path") or "/"


if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command(sys.argv[2], sys.argv[1])
    else:
        print client.command(sys.argv[1])
