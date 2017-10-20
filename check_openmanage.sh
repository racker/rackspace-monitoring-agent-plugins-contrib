#!/bin/bash

# Rackspace Cloud Monitoring Plug-In
# check_openmanage wrapper plugin to check health of Dell servers via OMSA

# ----------------------------------------------------------------------------
# "THE BEER-WARE LICENSE" (Revision 42):
# <nipsy@bitgnome.net> wrote this file.  As long as you retain this notice you
# can do whatever you want with this stuff. If we meet some day, and you think
# this stuff is worth it, you can buy me a beer in return.
# ----------------------------------------------------------------------------

# Depends on Dell's OMSA being installed along with Trond Hasle Amundsen's
# wonderful check_openmanage plugin for Nagios (avaiable via EPEL on RPM based
# distributions or directly from his web site:
# http://folk.uio.no/trondham/software/check_openmanage.html

# Usage:
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
#
# This plugin returns 1 metric:
#   - status : the exit status returned from the check_openmanage script
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# :set consecutiveCount=3
#
# if (metric['status'] >= 3) {
#   return new AlarmStatus(CRITICAL, '#{report}');
# }
#
# if (metric['status'] == 2) {
#   return new AlarmStatus(CRITICAL, '#{report}');
# }
#
# if (metric['status'] == 1) {
#   return new AlarmStatus(WARNING, '#{report}');
# }
#
# return new AlarmStatus(OK, '#{report}');
#
# Things to keep in mind:
#   - this plugin will try to find check_openmanage in one of the "normal" distribution
#     managed paths where it might reside, or the actual shell path as a last resort.
#   - by default, we're ignoring uncertified drive warnings.  Feel free to change that
#     if it's important in your environment.

# Previous version of this wrapper used an opt_args argument.  But given
# you can set arguments to pass via the Monitoring API, that has been
# replaced with $@ below.  You might want to update your check with
# something like the following:
#
# {
#   "details": {
#     "file": "check_openmanage.sh",
#     "args": [
#       "-b",
#       "pdisk_cert=all",
#       "-b",
#       "ctrl_fw=all"
#     ]
#   }
# }

search=(/usr/lib64/nagios/plugins /usr/lib/nagios/plugins)

for i in ${search[@]}; do
	if [[ -x ${i}/check_openmanage ]]; then
		check_cmd="${i}/check_openmanage"
		break
	fi
done

if [[ -z "${check_cmd}" ]]; then
	if ! check_cmd=$(which check_openmanage); then
		echo "status Could not find check_openmanage script!"
		exit 1
	fi
fi

report=$(${check_cmd} ${@})
status=$?

echo "status successfully ran check_openmanage wrapper plugin"
echo "metric status int32 ${status}"
echo "metric report string $(echo -E ${report} | head -1)"

exit 0
