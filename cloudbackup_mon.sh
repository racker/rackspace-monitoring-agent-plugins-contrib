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
# It needs to be passed 2-3 params by the backup system:
#
# apikey datacenter [backupid]
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

SYNOPSIS:  ./cloudbackup_mon.sh apikey datecenter [backup-configuration-id]
USAGE EXAMPLE: ./cloudbackup_mon.sh big_long_api_key iad

'datacenter' should be one of [iad ord syd dfw hkg] and must be lowercase

(sorry no support for 'lon' datacenter at this time)

HELP
        exit 0
}

if [ -z "$1" ]; then
        help
fi
api_key=$1

if [ -z "$2" ]; then
	help
else
	dc=$2
fi

if [ -z "$3" ]; then
	this_backup_conf_id=
else
	this_backup_conf_id=$2
fi


# Get username and agentid
username=`cat /etc/driveclient/bootstrap.json | grep Username | awk '{print $3}' | sed -e 's/"//g' -e 's/,//g'`
agentid=`cat /etc/driveclient/bootstrap.json | grep AgentId\" | awk '{print $3}' | sed -e 's/,//g'`

# Get token
json=`curl --data "{ \"auth\":{ \"RAX-KSKEY:apiKeyCredentials\":{ \"username\":\"${username}\", \"apiKey\":\"${api_key}\" } } }" -H "Content-Type: application/json" -X POST https://auth.api.rackspacecloud.com/v2.0/tokens`
token=`echo $json | python -m json.tool | grep token -A6 | grep id | cut -d\" -f4`
url=$(echo $json | python -m json.tool | grep backup | grep $dc | cut -d\" -f4)

# Get latest backup IDs
backup_ids=`curl -s -H "X-Auth-Token: $token" $url/backup-configuration/system/$agentid | python -m json.tool |grep LastRunBackupReportId | awk '{print $2}' | sed -e 's/,//g'`

tmpfile=`mktemp`
for backup_id in $backup_ids; do

  # Run report to see if backup was successful:
  curl -s -H "X-Auth-Token: $token " $url/backup/report/$backup_id | python -m json.tool > $tmpfile

  conf_id=`grep BackupConfigurationId < $tmpfile | sed -e 's/"BackupConfigurationId": //g' -e 's/,//g' -e 's/[ \t]*//g'`
  if [ "X$this_backup_conf_id" != "X" -a "X$conf_id" != "X$this_backup_conf_id" ]; then
    continue
  fi

  # Parse report
  name=`grep BackupConfigurationName < $tmpfile | sed -e 's/"BackupConfigurationName": "//g' | sed -e 's/",//g' -e 's/^[ \t]*//'`
  diagnostics=`grep Diagnostics < $tmpfile | sed -e 's/"Diagnostics": "//g' -e 's/",//g' -e 's/^[ \t]*//'`
  numerrors=`grep NumErrors < $tmpfile | awk '{print $2}' | sed -e 's/,//g'`
  reason=`grep Reason < $tmpfile | awk '{print $2}' | sed -e 's/,//g' -e 's/"//g'`
  state=`grep State < $tmpfile | awk '{print $2}' | sed -e 's/,//g' -e 's/"//g'`

  # Return numeric value that can be checked when report is missing fields
  if [ "X$numerrors" = "X" ]; then
    numerrors=0
  fi

  echo "metric diagnostics string $diagnostics"
  echo "metric numerrors int $numerrors"
  echo "metric reason string $reason"
  echo "metric state string $state"
  echo "metric backup_id int $backup_id"
  echo "metric backup_configuration_id int $conf_id"
  echo "metric backup_configuration_name string $name"
done

# Confirm agent is running on server
agent_check=`ps ax | grep -v grep | grep -v process_mon | grep -c "driveclient"`

# Generate metrics
echo "metric agent_running int $agent_check"

# Clean up
rm $tmpfile
