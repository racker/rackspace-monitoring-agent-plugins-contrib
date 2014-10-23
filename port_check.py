#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin to check port, particularly
useful for services that aren't accessible to a remote port check.

Copyright 2013 Steve Katen <steve.katen@rackspace.com>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys
import socket


def socket_open(host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((host, int(port)))
        s.shutdown(2)
        s.close()
    except socket.error:
        return "CLOSED"
    else:
        return "OPEN"


def main():
    if len(sys.argv) != 3:
        print "Usage: %s <host> <port>" % sys.argv[0]
        sys.exit(0)

    host = sys.argv[1]
    port = sys.argv[2]
    p = socket_open(host, port)

    if not p:
        print "status err no connection"
        sys.exit(0)

    print "status OK"
    print "metric port int", port
    print "metric status string", p


if __name__ == '__main__':
    main()
