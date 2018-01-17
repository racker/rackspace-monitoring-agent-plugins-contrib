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
#   return new AlarmStatus(CRITICAL, 'Errors found during last Cloud Backup: #{diagnostics}');
# }
# if (metric['reason'] != 'Success') {
#   return new AlarmStatus(CRITICAL, 'The last Cloud Backup was not successful.');
# }
# if (metric['state'] != 'Completed') {
#   return new AlarmStatus(CRITICAL, 'The last Cloud Backup was not completed.');
# }
# if (metric['agent_running'] == 0) {
#   return new AlarmStatus(CRITICAL, 'The Cloud Backup Agent is not running.');
# }
# if (metric['age'] > 129600) {
#   return new AlarmStatus(CRITICAL, 'The last Cloud Backup is more than 36 hours old!');
# }
# return new AlarmStatus(OK, 'The last Cloud Backup was successful.');

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
  this_backup_conf_id=$3
fi


# Get username and agentid
username=$(cat /etc/driveclient/bootstrap.json | grep Username | awk '{print $3}' | sed -e 's/"//g' -e 's/,//g')
agentid=$(cat /etc/driveclient/bootstrap.json | grep AgentId\" | awk '{print $3}' | sed -e 's/,//g')

# Get token
region=$(echo "$dc" | tr "A-Z" "a-z")
python_import="import sys,json;data=json.loads(sys.stdin.read());"
json=$(curl -s --data "{ \"auth\":{ \"RAX-KSKEY:apiKeyCredentials\":{ \"username\":\"${username}\", \"apiKey\":\"${api_key}\" } } }" -H "Content-Type: application/json" -X POST https://auth.api.rackspacecloud.com/v2.0/tokens)
token=$(echo "$json" | python -c "${python_import} print data['access']['token']['id']")
url=$(echo "$json" | python -c "${python_import} print(''.join([y['publicURL'] for y in [ x['endpoints'] for x in data['access']['serviceCatalog'] if x['name'] == 'cloudBackup' ][0] if y['region'].lower() == '$region' ]))")

# Get latest backup ID
filter="${this_backup_conf_id:+if x['BackupConfigurationId'] == $this_backup_conf_id}"
backup_config=$(curl -s -H "X-Auth-Token: $token" "$url/backup-configuration/system/$agentid" ) 
backup_config_ids=($(echo "$backup_config" | python -c "${python_import} print (' '.join([str(x['BackupConfigurationId']) for x in data $filter]))"))
backup_id=($(echo "$backup_config" | python -c "${python_import} print (' '.join([str(x['LastRunBackupReportId']) for x in data $filter]))"))

if [ ${#backup_id[@]} -eq 1 -a "[$backup_id]" != "[None]" ]; then
  # Run report to see if backup was successful:
  report=$(curl -s -H "X-Auth-Token: $token" "$url/backup/report/$backup_id")
  
  conf_id=$(echo "$report" | python -c "${python_import} print data['BackupConfigurationId']")

  # Parse report
  name=$(echo "$report" | python -c "${python_import} print data['BackupConfigurationName']")
  diagnostics=$(echo "$report" | python -c "${python_import} print data['Diagnostics']")
  numerrors=$(echo "$report" | python -c "${python_import} print data['NumErrors']")
  reason=$(echo "$report" | python -c "${python_import} print data['Reason']")
  state=$(echo "$report" | python -c "${python_import} print data['State']")
  start_time=$(echo "$report" | python -c "${python_import} import re; print int(int(re.search(\"\\d+\", data['StartTime']).group(0))/1000)")
  now=$(date '+%s')
  age=$(( $now - $start_time ))
  
  # Return numeric value that can be checked when report is missing fields
  if [ "X$numerrors" = "X" ]; then
    numerrors=0
  fi
elif [ ${#backup_id[@]} -gt 1 ]; then
  diagnostics=$(echo "Specify the backup-configuration-id in the argument. Multiple backup configs found: [[ ${backup_config_ids[@]} ]]")
else
  diagnostics="No backups configurations or backups found"
fi

diagnostics=$(echo "$diagnostics" | cut -c -128)
echo "metric diagnostics string ${diagnostics:-Error: No data}"
echo "metric numerrors int ${numerrors:--1}"
echo "metric reason string ${reason:-Error: No data}"
echo "metric state string ${state:-Error: No data}"
echo "metric backup_id int ${backup_id:--1}"
echo "metric backup_configuration_id int ${conf_id:--1}"
echo "metric backup_configuration_name string ${name:-Error: No data}"
echo "metric start_time uint64 ${start_time:--1}"
echo "metric age uint64 ${age:--1}"

# Confirm agent is running on server
agent_check=$(ps ax | grep -v grep | grep -v process_mon | grep -c "driveclient")

# Generate metrics
echo "metric agent_running int $agent_check"
