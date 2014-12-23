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
# REQUIRES 'bc' to be installed

SERVICE="lsyncd"

# Attempt to locate lsyncd configuration file
if [ -e /etc/lsyncd.lua ]; then
	lsyncd_conf_file="/etc/lsyncd.lua"
elif [ -e /etc/lsyncd.conf ]; then
	lsyncd_conf_file="/etc/lsyncd.conf"
elif [ -e /etc/lsyncd/lsyncd.conf.lua ]; then
        lsyncd_conf_file="/etc/lsyncd/lsyncd.conf.lua"
elif [ -e /etc/lsyncd/lsyncd.conf ]; then
        lsyncd_conf_file="/etc/lsyncd/lsyncd.conf"
else
	echo "status ${SERVICE} not installed"
	exit 1
fi

# Test if the service is running
RESULT=$(pgrep -x ${SERVICE})
if [[ "${RESULT:-null}" = null ]]; then
	echo "metric ${SERVICE}_status string notrunning"
else
	echo "metric ${SERVICE}_status string running"
fi

# Calculate current inotify watches
current_inotify_watches=$(awk '{print $3}' <(sysctl fs.inotify.max_user_watches))

# 2.1.x status file contains number of directories watched.  Avoids I/O overhead of find command.
lsyncd_status_file=$(sed -n 's/.*statusFile\s*=\s*"\(.*\)",.*/\1/p' $lsyncd_conf_file)
if [ -e "$lsyncd_status_file" ]; then
	current_directories_to_watch=$(sed -n "s/Inotify watching \([0-9][0-9]*\) directories/\1/p" "$lsyncd_status_file")
fi

# Fall back to old method if current_directories_to_watch is not a number
if ! [[ "$current_directories_to_watch" =~ ^[0-9]+$ ]] ; then
	# Store the values we pull from the configuration file to an array
	watch_list=()
	for dir_watch in $(grep "source=\"/" ${lsyncd_conf_file} | grep -ve '^[ ]*--' ); do
		current_dir=$(echo $dir_watch | cut -d'=' -f2| sed -e "s/\"//g" -e "s/,//g")
		watch_list=("${watch_list[@]}" "${current_dir}")
	done
	# Force unique values in this array - not calculating for multiple directories
	sorted_unique_dirs=$(echo "${watch_list[@]}" | tr ' ' '\n' | sort -u | tr '\n' ' ')
	# calculate current directories to watch
	current_directories_to_watch=0
	for SOURCE in ${sorted_unique_dirs[@]}; do
		current_directories_to_watch=$(echo ${current_directories_to_watch}+$(find ${SOURCE} -type d | wc -l | awk '{print $1}') | bc -l)
	done
	#current_directories_to_watch=$(find ${SOURCE} -type d | wc -l | awk '{print $1}')
fi

# calculate percenentage of total
current_percentage=$(echo "${current_directories_to_watch}/${current_inotify_watches}" | bc -l | awk '{printf "%f", $1*100}')

echo "metric percent_used_watches double ${current_percentage}"

