#!/bin/bash
#
# Rackspace Cloud Monitoring Plug-In
# Check the mtime of a file and how long it has been since it has been modified
#
# (c) 2015 Justin Gallardo <justin.gallardo@gmail.com>
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
# It accepts one argument, which should be the file you wish to check the mtime of.
#
# Returns 2 metrics:
#  - mtime: The time(unix epoch) the file was last modified
#  - age: The number of seconds that have elapsed since the file was modified
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['age'] > 3600) {
#  return new AlarmStatus(CRITICAL, 'The file has not been modified in more than 1 hour. Last modified #{age} seconds ago');
# }
# return new AlarmStatus(OK, 'The file was last modified #{age} seconds ago.');
#
file=$1

if [ ! -e $file ]; then
  echo "status critical \"$file\" does not exist"
  exit 1
fi

if [ ! -r $file ]; then
  echo "status critical \"$file\" is not readable"
  exit 1
fi

mtime=$(stat -c%Y $file)
now=$(date '+%s')
age=$(( $now - $mtime ))

echo "status ok file statted"
echo "metric mtime uint64 $mtime"
echo "metric age uint64 $age seconds"
exit 0
