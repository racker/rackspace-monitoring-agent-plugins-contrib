#!/usr/bin/env bash
#
# process_mon.sh
# Rackspace Cloud Monitoring Plugin to check if process is running.
#
# Copyright (c) 2013, Stephen Lang <stephen.lang@rackspace.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
# Curl Command:
# curl -i -X POST -H 'Host: monitoring.api.rackspacecloud.com' -H
# 'Accept-Encoding: gzip,deflate' -H 'X-Auth-Token: YOUR_API_TOKEN' -H
# 'Content-Type: application/json; charset=UTF-8' -H 'Accept:
# application/json' --data-binary '{"label": "Process Check", "type":
# "agent.plugin", "details": {"args": ["PROCESS_NAME"],"file":
# "process_mon.sh"}}'  --compress
# 'https://monitoring.api.rackspacecloud.com:443/v1.0/YOUR_ACCOUNT/entities/YOUR_ENTITY/checks'
#
# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['process_mon'] == 0) {
# return new AlarmStatus(CRITICAL, 'Process not running.');
# }
#
# if (metric['process_age'] > 86400) {
#   return new AlarmStatus(WARNING, 'Process has been running for over 24 hours.');
# }
#
# return new AlarmStatus(OK, 'Process running normally.');

function help {

cat <<HELP

SYNOPSIS:  ./process_mon.sh [process]...
USAGE EXAMPLE: ./process_mon.sh lsync

HELP
        exit 0
}

if [ -z "$1" ]; then
        help
fi

process_check=`ps ax | grep -v grep | grep -v process_mon | grep -c "$1"`
process_pid=`ps ax | grep -v grep | grep -v process_mon | grep "$1" | head -n 1 | awk '{print $1}'`
if (( $process_check > 0 )); then
  process_age=`ps -o etimes= -p "$process_pid"`
  process_age=${process_age## }
fi

echo "metric process_mon int $process_check"
echo "metric process_pid int ${process_pid:-0}"
echo "metric process_age int ${process_age:-0}"

exit 0