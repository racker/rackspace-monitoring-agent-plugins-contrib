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
# if (metric['code'] != 200) {
#  return new AlarmStatus(CRITICAL, '#{code} response received.  Expected 200.');
# }
# return new AlarmStatus(OK, '200 response received');
#

response=`curl -s -o /dev/null -ILk -w "%{http_code} %{time_connect} %{time_total} %{url_effective}" $1`
code=`echo $response | awk {'print $1'}`
time_connect=`echo $response | awk {'print $2'}`
time_total=`echo $response | awk {'print $3'}`
url=`echo $response | awk {'print $4'}`

echo "status ok connection made"
echo "metric code uint32 $code"
echo "metric time_connect double $time_connect"
echo "metric time_total double $time_total"
echo "metric url string $url"
