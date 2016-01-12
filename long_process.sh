#!/usr/bin/env bash
#
# long_process.sh
# Rackspace Cloud Monitoring Plugin to check if a process is running for too
# long.
#
# Author Mark Garratt <mgarratt@gmail.com>
# Copyright (c) 2016, Horizon Discovery Plc.
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
# application/json' --data-binary '{"label": "Long Process Check", "type":
# "agent.plugin", "details": {"args": ["PROCESS_NAME", "TIMEOUT"],"file":
# "long_process.sh"}}'  --compress
# 'https://monitoring.api.rackspacecloud.com:443/v1.0/YOUR_ACCOUNT/entities/YOUR_ENTITY/checks'
#
# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['numprocs'] > 0) {
#     return new AlarmStatus(CRITICAL, '#{numprocs} long running processes(s): #{pids}');
# }
#
# return new AlarmStatus(OK, 'No long running processes.');

if [ "$#" -ne 2 ]; then
    cat <<HELP

    SYNOPSIS: ./long_process.sh [process] [age_in_mins]
    USAGE EXAMPLE: ./long_process.sh "./cron.php" 30

HELP
exit 0
fi

set -o pipefail

# Timestamp to determine what is long running
CUTOFF=$(date -d "$2 minutes ago" +'%s')
# Get a list of long running PIDs, without displaying output
{
    PIDS=$(
        # Get running processes
        ps ax -o lstart,pid,args | \
        # Grep out unwanted processes
        grep -v grep | \
        grep ""$1"" | \
        # Convert date to timestamp and print if less than (before) CUTOFF
        awk '{
            cmd=sprintf("date -d \"%s %s %s %s %s\" +%%s", $1, $2, $3, $4, $5);
            cmd | getline tstamp;
            if (tstamp < "'"$CUTOFF"'") printf("%s ", $6);
        }' | \
        # Remove trailing space
        sed -e 's/[[:space:]]*$//'
    )
} &> /dev/null

# Check for a failure in the pipe
PIPEEXIT=$?
if [ $PIPEEXIT -ne 0 ]; then
    echo "status Fail"
    exit $PIPEEXIT
fi

# Numeric metric to compare against (number of processes)
# Convert to array and count
NUMPROCS=($PIDS)
NUMPROCS=${#NUMPROCS[@]}

echo "status Success"
echo "metric numprocs int $NUMPROCS"
if [ $NUMPROCS -ne 0 ]; then
    echo "metric pids string $PIDS"
else
    echo "metric pids string -"
fi
