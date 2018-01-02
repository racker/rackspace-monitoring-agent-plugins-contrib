#!/bin/bash
#
# Rackspace Cloud Monitoring Plug-In
# Check that a mounted filesystem is mounted
#
# (c) 2017 Teddy Caddy <github.com/tcaddy>
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
# It accepts two arguments:
#  - path: the path of the mount point you want to check
#  - flag_file: (optional) check that a flag file exists and is readable
#
# Returns 5 metrics:
#  - path: the input path paramter
#  - flag_file: the input flag_file parameter
#  - mounted: returns 1 if mount point is mounted
#  - flag_file_exists: returns 1 if flag file exists
#  - flag_file_readable: returns 1 if flag file is readable
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['mounted'] != 1) {
#   return new AlarmStatus(CRITICAL, 'The mount point is not mounted: #{path}');
# }

# if (metric['flag_file'] != '' && metric['flag_file_exists'] != 1) {
#   return new AlarmStatus(CRITICAL, 'The flag file does not exist: #{path}/#{flag_file}');
# }

# if (metric['flag_file'] != '' && metric['flag_file_readable'] != 1) {
#   return new AlarmStatus(CRITICAL, 'The flag file is not readable: #{path}/#{flag_file}');
# }

# return new AlarmStatus(OK, 'The mount point is OK: #{path}');
#
path=$1
flag_file="$1/$2"

mounted=0
flag_file_exists=0
flag_file_readable=0

if [ -d $path ]; then
  mounts=$(cat /proc/mounts)
  if [[ $mounts == *"$path"* ]]; then
    mounted=1
    if [ ! -z "${2// }" ]; then
      if [ -e $flag_file ]; then
        flag_file_exists=1
        if [ -r $flag_file ]; then
          flag_file_readable=1
          exit_status=0
        else
          exit_status=1
        fi
      else
        exit_status=1
      fi
    fi
  else
    exit_status=1
  fi
else
  exit_status=1
fi

echo "metric path string $path"
echo "metric flag_file string $2"
echo "metric mounted int64 $mounted"
echo "metric flag_file_exists int64 $flag_file_exists"
echo "metric flag_file_readable int64 $flag_file_readable"
exit $exit_status
