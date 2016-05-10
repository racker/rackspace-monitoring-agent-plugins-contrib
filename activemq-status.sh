#!/bin/bash
#
# Description: Custom plugin which checks activemq status.

# Copyright 2013 Ted Neykov
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Looks for 'CurrentStatus' line in output of `activemq-admin query` command.
# Query command can return multiple lines containing 'CurrentStatus'.
# Returns non-zero and 'status error' if any of the lines are not 'CurrentStatus = Good'.

# Look for the activemq-admin script in /opt
amq_bin=$(find /opt/ -name 'activemq-admin' | egrep '/bin/activemq-admin')

if [ -z $amq_bin ]; then
  echo "status error: Could not find activemq-admin."
  exit 1
fi

amq_query=`"$amq_bin" query`
curr_status=`echo "$amq_query" | grep CurrentStatus`

echo "$curr_status" |
while read -r line; do
  line_status=`echo "$line" | awk '{print $3}'`
  if [ "$line_status" == 'Good' ]; then
    :
  else
    # Found non "Good" status or empty line
    exit 1
  fi
done

if [ $? -eq 0 ]; then
  echo "status good"
else
 echo "status error"
 exit 1
fi
