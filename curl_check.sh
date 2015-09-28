#!/bin/bash
#
# Rackspace Cloud Monitoring Plug-In
# Simple curl request test that can be used to query internal hosts
#
# (C)2014 James Buchan <james.buchan@rackspace.com>
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# It accepts one argument, which should be the site you wish to query.
# 
# Returns 4 metrics:
#  - code: The final status code returned
#  - time_connect: The total time, in seconds, that the full operation lasted
#  - time_total: The time, in seconds, it took from the start until the TCP 
#                connect to the remote host (or proxy) was completed
#  - url: The last URL that was queried (if redirects occurred)
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['code'] != '200') {
#  return new AlarmStatus(CRITICAL, '#{code} response received.  Expected 200.');
# }
# return new AlarmStatus(OK, '200 response received');
#

function extract_header()
{
    ret=$(echo "$1" | grep "$2:" | tail -1 | cut -d' ' -f 2- | tr -d '\n\r' )
    [ -n "$ret" ] && echo -n $ret
}

response=$(curl -sS -L -f -I -w "Response-Code: %{response_code}\nTime-Connect: %{time_connect}\nTime-Total: %{time_total}\nURL-Effective: %{url_effective}\n" $1 2>&1)

if [ $? -eq 0 ]
then
  echo "status ok connection made"
  echo "metric code string $(extract_header "$response" Response-Code)"
  echo "metric time_connect double $(extract_header "$response" Time-Connect) seconds"
  echo "metric time_total double $(extract_header "$response" Time-Total) seconds"
  echo "metric url string $(extract_header "$response" URL-Effective)"

  etag=$(extract_header "$response" ETag)
  [ -n "$etag" ] && echo "metric etag string $etag"

  length=$(extract_header "$response" Content-Length)
  [ -n "$length" ] && echo "metric content_length uint32 $length bytes"

  modified=$(extract_header "$response" Last-Modified)
  if [ -n "$modified" ]
  then
      modified_seconds=$(date --date="$modified" +"%s")
      age=$(($(date +"%s") - $modified_seconds))
      echo "metric page_age uint64 $age seconds"
  fi

  exit 0
else
  #remove statistics from our status line, only keep the error
  echo "status $(echo $response | awk -F'000 ' '{$0=$1}1' )"
fi

exit 1
