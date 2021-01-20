#!/bin/bash
#
# Description: Custom plugin which checks that some service is listening on the
# specified port.
# Author: Tomaz Muraus
# License: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

if [ $# -ne 3 ]; then
  echo "Usage: $0 <tcp|udp> <ip> <port>"
  exit 100
fi

PROTOCOL=$1
IP=$2
PORT=$3

OPTIONS=""

if [ $PROTOCOL = "udp" ]; then
    OPTIONS="-u"
fi

nc -zw 1 ${OPTIONS} ${IP} ${PORT} < /dev/null > /dev/null 2>&1

if [ $? -ne 0 ]; then
    echo "status Nothing listening on port ${IP}:${PORT} (${PROTOCOL})"
    echo "metric listening string no"
else
    echo "status Service listening on ${IP}:${PORT} (${PROTOCOL})"
    echo "metric listening string yes"
fi
