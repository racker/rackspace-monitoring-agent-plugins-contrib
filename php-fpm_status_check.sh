#!/bin/bash
# Copyright 2016 gustavo panizzo <gustavo.panizzo@rackspace.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -----
#
# This plugin monitors the metrics produced by the PHP-FPM status page
# pm.status_path needs to be enabled per pool you want to monitor
#
# pm.status_path = /status-for-php-fpm
#
# and you need the cgi-fcgi command
# yum install fcgi
# apt-get install libfcgi0ldbl
#
# For more info see:
#
# http://php.net/manual/en/install.fpm.configuration.php
#
# By default the monitor fails if the check does not complete successfully.
#
# Metrics for:
#
# accepted conn
# listen queue
# max listen queue
# listen queue len
# idle processes
# active processes
# total processes
# max active processes
# max children reached
#
# are also reported.
#
#
# Usage:
# Place script in /usr/lib/rackspace-monitoring-agent/plugins.
# Ensure file is executable (755).
#
# Set up a Cloud Monitoring Check of type agent.plugin to run
#
# php-fpm_status_check.sh SOCKET_PATH STATUS_URL
#
# Both are optional and default to:
#
#  /var/run/php-fpm/www.sock
#  /status-for-php-fpm
#
# There is no need to define specific custom alert criteria.
# As stated, the monitor fails if the metrics cannot be collected.
# It is possible to define custom alert criteria with the reported
# metrics if desired.
#
# Example criteria :
#
#if (metric['max_children_reached'] > 0) {
#        return CRITICAL, "Max Children reached"
#}
#if (metric['legacy_state'] != 'ok') {
#        return CRITICAL, "PHP-PFM is not running correctly or misconfigured check"
#}
#
#return OK, "PHP-FPM is running correctly"


CGIFCGI=$(which cgi-fcgi 2>/dev/null)
if [ $? != 0 ]; then
  #echo "status error: Could not find cgi-fcgi."
  #echo "status error"
  echo "status err failed to obtain metrics."
  exit 1
fi

SOCKET=${1-/var/run/php-fpm/www.sock}
STATUS_PATH=${2-/status-for-php-fpm}
OUTPUT=$(mktemp)

SCRIPT_NAME="${STATUS_PATH}" SCRIPT_FILENAME="${STATUS_PATH}"  REQUEST_METHOD=GET $CGIFCGI -bind -connect ${SOCKET} 2>/dev/null > $OUTPUT
if [ $? != 0 ]; then
    #echo "status error"
    echo "status err failed to obtain metrics."
    exit 1
fi

accepted_conn=$(grep "^accepted conn:" $OUTPUT | awk '{print $3}') 2>/dev/null
listen_queue=$(grep "^listen queue:" $OUTPUT | awk '{print $3}') 2>/dev/null
max_listen_queue=$(grep "^max listen queue:" $OUTPUT | awk '{print $4}') 2>/dev/null
listen_queue_len=$(grep "^listen queue len:" $OUTPUT | awk '{print $4}') 2>/dev/null
idle_processes=$(grep "^idle processes:" $OUTPUT | awk '{print $3}') 2>/dev/null
active_processes=$(grep "^active processes:" $OUTPUT | awk '{print $3}') 2>/dev/null
total_processes=$(grep "^total processes:" $OUTPUT | awk '{print $3}') 2>/dev/null
max_active_processes=$(grep "^max active processes:" $OUTPUT | awk '{print $4}') 2>/dev/null
max_children_reached=$(grep "^max children reached:" $OUTPUT | awk '{print $4}') 2>/dev/null

echo "status ok succeeded in obtaining metrics."
echo "metric accepted_conn uint32 $accepted_conn"
echo "metric listen_queue uint32 $listen_queue"
echo "metric max_listen_queue uint32 $max_listen_queue"
echo "metric listen_queue_len uint32 $listen_queue_len"
echo "metric idle_processes uint32 $idle_processes"
echo "metric active_processes uint32 $active_processes"
echo "metric total_processes uint32 $total_processes"
echo "metric max_active_processes uint32 $max_active_processes"
echo "metric max_children_reached uint32 $max_children_reached"

rm -f $OUTPUT
exit 0
