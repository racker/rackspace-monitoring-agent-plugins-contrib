#!/bin/bash

# lsyncd-status.sh
# Rackspace Cloud Monitoring Plugin to verify the current return status of lsyncd.
#
# Copyright (c) 2013, Lindsey Anderson <lindsey.anderson@rackspace.com>
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
# See https://github.com/robszumski/rackspace-monitoring-varnish for a readme
# and more information
#
# Verify the current status of lsyncd
# *****************
# Note this data may take a few minutes to populate metric data at first
# *****************
#
# Example criteria :
#
# if (metric['lsyncd_status'] != 'running') {
#   return new AlarmStatus(CRITICAL, 'Lsyncd Service is NOT running.');
# }
# 
# if (metric['lsyncd_status'] == 'running' && metric['percent_used_watches'] >= 80) {
#   return new AlarmStatus(WARNING, 'Lsyncd is running but the number of directories has reached 80% of notify watches.');
# }
# 
# if (metric['lsyncd_status'] == 'running' && metric['percent_used_watches'] >= 95) {
#   return new AlarmStatus(CRITICAL, 'Lsyncd is running but the number of directories has reached 95% of notify watches.');
# }
#
# return new AlarmStatus(OK, 'Lsyncd Service is running.');
#


SERVICE="lsyncd"
RESULT=$(pgrep ${SERVICE})
if [[ "${RESULT:-null}" = null ]]; then
	echo "metric ${SERVICE}_status string notrunning"
else
	echo "metric ${SERVICE}_status string running"
fi

# Calculate current inotify watches
current_inotify_watches=$(awk '{print $3}' <(sysctl fs.inotify.max_user_watches))
# Update this value based on the current lsyncd version, the standard will use 2.1.x
# Currently only taking first value, assuming replicated for multiple nodes
# This value may need to be modified based on the amount of different directories being
# watched
if [ -e /etc/lsyncd.lua ]; then
	SOURCE=$(grep "source" /etc/lsyncd.lua | head -1 | cut -d'=' -f2 | sed -e "s/\"//g" -e "s/,//g")
elif [ -e /etc/lsyncd.conf ]; then
	SOURCE=$(grep "source" /etc/lsyncd.conf | head -1 | cut -d'=' -f2 | sed -e "s/\"//g" -e "s/,//g")
else
	echo "status ${SERVICE} not installed"
fi
# calculate current directories to watch
current_directories_to_watch=$(find ${SOURCE} -type d | wc -l | awk '{print $1}')
# calculate percenentage of total
current_percentage=$(echo "${current_directories_to_watch}/${current_inotify_watches}" | bc -l | awk '{printf "%f", $1*100}')

echo "metric percent_used_watches double ${current_percentage}"

