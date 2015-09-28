#!/bin/bash
#
# Name: redis_slave_count.sh
# Description: Custom plugin that returns number of slaves connected to redis.

# Copyright 2014 Zachary Deptawa
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

# SYNOPSIS:  ./redis_slave_count.sh [host] [port] [password]... 
# USAGE EXAMPLE: ./redis_slave_count.sh 127.0.0.1 6379 abcdef12
#
# Note: If no host/port/password given, it will default to host 0.0.0.0, port 6379, no pass.

# What the plugin does:
# - Looks for 'connected_slaves' line in output of `redis-cli INFO` command and
#   returns that value as a metric.
# - Returns non-zero and 'status error' if 'connected_slaves' not found.

# Rackspace Cloud Monitoring Plugin Usage:
# - Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins.
# - Create a check that calls this plugin.
# - Pass 'args' as 'host port' or 'host port pass' if needed.
#   NOTE: If you are unable to create the check, make sure you're
#   passing the args as an array!
# - Create an alarm based on the criteria you're looking for.
#
# The following is an example 'criteria' for a Rackspace Cloud Monitoring Alarm:
#
# if (metric['connected_slaves'] == 0) {
# return new AlarmStatus(CRITICAL, 'No slaves connected.');
# }
#
# return new AlarmStatus(OK, 'Slaves are connected.');


# If host arg is set, set $HOST. Else, default $HOST to '0.0.0.0'.
if [ $1 ]; then
  HOST=$1
else
  HOST=0.0.0.0
fi

# If port arg is set, set $PORT. Else, default $PORT to '6379'.
if [ $2 ]; then
  PORT=$2
else
  PORT=6379
fi

if [ $3 ]; then
  PASS=$3
fi

# Get the info and connected_slaves output.
if [ $3 ]; then
  INFO=`redis-cli -h $HOST -p $PORT -a $PASS INFO`
  SLAVE_COUNT=`redis-cli -h $HOST -p $PORT -a $PASS INFO |grep connected_slaves |awk -F':' {'print$2'}`
else
  INFO=`redis-cli -h $HOST -p $PORT INFO`
  SLAVE_COUNT=`redis-cli -h $HOST -p $PORT INFO |grep connected_slaves |awk -F':' {'print$2'}`
fi

# If $SLAVE_COUNT, return metrics. Else fail.
if [ $SLAVE_COUNT ]; then
  echo "metric connected_slaves int $SLAVE_COUNT"
else
  echo "status error - unable to pull stats from redis INFO"
  exit 1
fi
