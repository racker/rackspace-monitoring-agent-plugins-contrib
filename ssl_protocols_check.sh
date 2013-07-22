#!/usr/bin/env bash
#
# Description: Agent plugin which detects supported SSL / TLS protocol versions.
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

if [ $# -ne 1 ] && [ $# -ne 2 ]; then
  echo "Usage: $0 <ip> [port]"
  exit 100
fi

IP=$1

if [ $# -eq 2 ]; then
    PORT=$2
else
    PORT=443
fi

SUPPORTED_PROTOCOLS=()

OUTPUT=$(openssl s_client -ssl2 -connect ${IP}:${PORT} < /dev/null 2>&1)

if grep -q "DONE " <<< ${OUTPUT}; then
    SUPPORTED_PROTOCOLS[${#SUPPORTED_PROTOCOLS[@]}]="ssl_2_0"
    echo "metric ssl_2_0 string yes"
elif grep -q "wrong version number" <<< ${OUTPUT}; then
    echo "metric ssl_2_0 string no"
elif grep -q "unknown option" <<< ${OUTPUT}; then
    echo "openssl doesn't support SSL v2.0, probably using openssl >= 1.0.0" >&2
    echo "metric ssl_2_0 string unknown"
fi

OUTPUT=$(openssl s_client -ssl3 -connect ${IP}:${PORT} < /dev/null 2>&1)

if grep -q "DONE" <<< ${OUTPUT}; then
    SUPPORTED_PROTOCOLS[${#SUPPORTED_PROTOCOLS[@]}]="ssl_3_0"
    echo "metric ssl_3_0 string yes"
elif grep -q "wrong version number" <<< ${OUTPUT}; then
    echo "metric ssl_3_0 string no"
elif grep -q "unknown option " <<< ${OUTPUT}; then
    echo "metric ssl_3_0 string unknown"
fi

OUTPUT=$(openssl s_client -tls1 -connect ${IP}:${PORT} < /dev/null 2>&1)

if grep -q "DONE" <<< ${OUTPUT}; then
    SUPPORTED_PROTOCOLS[${#SUPPORTED_PROTOCOLS[@]}]="tls_1_0"
    echo "metric tls_1_0 string yes"
elif grep -q "wrong version number" <<< ${OUTPUT}; then
    echo "metric tls_1_0 string no"
elif grep -q "unknown option " <<< ${OUTPUT}; then
    echo "metric tls_1_0 string unknown"
fi

OUTPUT=$(openssl s_client -tls1_1 -connect ${IP}:${PORT} < /dev/null 2>&1)

if grep -q "DONE" <<< ${OUTPUT}; then
    SUPPORTED_PROTOCOLS[${#SUPPORTED_PROTOCOLS[@]}]="tls_1_1"
    echo "metric tls_1_1 string yes"
elif grep -q "wrong version number" <<< ${OUTPUT}; then
    echo "metric tls_1_1 string no"
elif grep -q "unknown option " <<< ${OUTPUT}; then
    echo "openssl doesn't support TLS v1.1, probably using openssl < 1.0.0" >&2
    echo "metric tls_1_1 string unknown"
fi

OUTPUT=$(openssl s_client -tls1_2 -connect ${IP}:${PORT} < /dev/null 2>&1)

if grep -q "DONE" <<< ${OUTPUT}; then
    SUPPORTED_PROTOCOLS[${#SUPPORTED_PROTOCOLS[@]}]="tls_1_2"
    echo "metric tls_1_2 string yes"
elif grep -q "wrong version number" <<< ${OUTPUT}; then
    echo "metric tls_1_2 string no"
elif grep -q "unknown option " <<< ${OUTPUT}; then
    echo "openssl doesn't support TLS v1.2, probably using openssl < 1.0.0" >&2
    echo "metric tls_1_2 string unknown"
fi

SUPPORTED_PROTOCOLS=$(IFS=$','; echo "${SUPPORTED_PROTOCOLS[*]}")
echo "status Supported protocols: ${SUPPORTED_PROTOCOLS}"
