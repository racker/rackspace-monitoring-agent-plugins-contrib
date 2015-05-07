#!/usr/bin/env bash
#
# cloudbackup_mon.sh
# Rackspace Cloud Monitoring Plugin to help detect if there are
# problems with Cloud Backups.
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
# 'Accept-Encoding: gzip,deflate' -H 'X-Auth-Token: YOUR_API_TOKEN'
# -H 'Content-Type: application/json; charset=UTF-8' -H 'Accept: application/json'
# --data-binary '{"label": "Cloud Backup Check", "type": "agent.plugin", "details":
# {"args": ["YOUR_API_KEY"],"file": "cloudbackup_mon.sh"}}'  --compress
# 'https://monitoring.api.rackspacecloud.com:443/v1.0/YOUR_ACCOUNT/entities/YOUR_ENTITY/checks'
#
# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['diagnostics'] != 'No errors') {
# return new AlarmStatus(CRITICAL, 'Errors found during last backup run.');
# }
# if (metric['reason'] != 'Success') {
# return new AlarmStatus(CRITICAL, 'Last backup was not successful.');
# }
# if (metric['state'] != 'Completed') {
# return new AlarmStatus(CRITICAL, 'The last backup was not completed.');
# }
# if (metric['agent_running'] == 0) {
# return new AlarmStatus(CRITICAL, 'Agent is not running.');
# }
#
# return new AlarmStatus(OK, 'Cloud Backups Successful.');

function help {

cat <<HELP

SYNOPSIS:  ./cloudbackup_mon.sh [apikey]...
USAGE EXAMPLE: ./cloudbackup_mon.sh 4fdd665dfddwgfdvfnotreal

HELP
        exit 0
}


function error_exit {
    #   ----------------------------------------------------------------
    #   Function for exit due to fatal program error
    #       Accepts 1 argument:
    #           string containing descriptive error message
    #   ----------------------------------------------------------------

    echo "status ${1:-"Unknown Error"}" 1>&2
    exit 1
}

if [ -z "$1" ]; then
        help
fi

# Get username and agentid
username=`cat /etc/driveclient/bootstrap.json | grep Username | awk '{print $3}' | sed -e 's/"//g' | sed -e 's/,//g'`
agentid=`cat /etc/driveclient/bootstrap.json | grep AgentId | awk '{print $3}' | sed -e 's/,//g'`

# Get token
token=`curl -s -I -H "X-Auth-Key: $1" -H "X-Auth-User: $username" https://auth.api.rackspacecloud.com/v1.0 | grep X-Auth-Token |awk {'print $2'}`
    [[ -z "$token" ]] && error_exit "failed to set token"

# Get report ID:
last_report=`curl -s -H "X-Auth-Token: $token" https://backup.api.rackspacecloud.com/v1.0/backup-configuration/system/$agentid | python -m json.tool |grep LastRunBackupReportId | awk '{print $2}' | sed -e 's/,//g'`
    [[ -z "$token" ]] && error_exit "failed to set last_report"

# Run report to see if backup successful:
curl -s -H "X-Auth-Token: $token " https://backup.api.rackspacecloud.com/v1.0/backup/report/$last_report \
    | python -m json.tool 2>/dev/null > report.tmp \
    || error_exit "failed to get last_report"

# Parse report
diagnostics=`cat report.tmp | grep Diagnostics | sed -e 's/"Diagnostics": "//g' | sed -e 's/",//g' | sed -e 's/^[ \t]*//'`
numerrors=`cat report.tmp | grep NumErrors | awk '{print $2}' | sed -e 's/,//g'`
reason=`cat report.tmp | grep Reason | awk '{print $2}' | sed -e 's/,//g' | sed -e 's/"//g'`
state=`cat report.tmp | grep State | awk '{print $2}' | sed -e 's/,//g' | sed -e 's/"//g'`

# Confirm agent is running on server
agent_check=`ps ax | grep -v grep | grep -v process_mon | grep -c "driveclient"`
    [[ -z "$agent_check" ]] && error_exit "failed to check agent status"

# Generate metrics
echo "metric diagnostics string $diagnostics"
echo "metric numerrors int $numerrors"
echo "metric reason string $reason"
echo "metric state string $state"
echo "metric agent_running int $agent_check"

# Clean up
rm report.tmp || error_exit "failed to cleanup report.tmp"

echo "status success"

exit 0
