#!/bin/bash

# Rackspace Cloud Monitoring plugin to check if a ssl cert is expired.

# Example:
# $ ./ssl_cert_expiration.sh <host> <port>

# Example Alarm Criteria:
# if (metric['cert_end_in'] <= 0) {
#	return new AlarmStatus(CRITICAL, 'Certificate has expired on host')
# }
# if (metric['cert_end_in'] < 604800) {
#   return new AlarmStatus(WARNING, 'Certificate expires in less than 1 week');
# }
# return new AlarmStatus(OK, 'Certificate valid for more than 1 week');

# Copyright 2015 Rackspace

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

if [ $# -ne 2 ]; then
  echo "Usage: $0 <host> <port>"
  exit 100
fi

HOST=$1
PORT=$2

EXPIRATION_DATE=$(echo ""|openssl s_client -connect $HOST:$PORT 2>/dev/null | openssl x509 -noout -enddate | sed 's/^not.*\=//')

REMAINING_SECONDS=$(( $(date -u -d"$EXPIRATION_DATE" +%s) - $(date +%s) ))

echo "status ok"
echo "metric cert_end_in int ${REMAINING_SECONDS}"
