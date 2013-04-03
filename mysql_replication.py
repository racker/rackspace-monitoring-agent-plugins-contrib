#!/usr/bin/env python

## Rackspace Cloud Monitoring Plug-In
## MySQL Replication State Validation
#
# (C)2013 Chris Mecca <chris.mecca@rackspace.com>
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
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
# if (metric['SLAVE_STATUS'] != 'ONLINE') {
#   return new AlarmStatus(CRITICAL, 'MySQL Replication is OFFLINE.');
# }
#
# if (metric['SLAVE_STATUS'] == 'ONLINE' && metric['SECONDS_BEHIND_MASTER'] \
#       >= 120 && metric['SECONDS_BEHIND_MASTER'] < 300) {
#   return new AlarmStatus(WARNING, 'MySQL Replication ONLINE \
#       but Slave is more than 2 minutes behind Master.');
# }
#
# if (metric['SLAVE_STATUS'] == 'ONLINE' && metric['SECONDS_BEHIND_MASTER'] \
#       >= 300) {
#   return new AlarmStatus(CRITICAL, 'MySQL Replication ONLINE \
#       but Slave is more than 5 minutes behind Master.');
# }
#
# return new AlarmStatus(OK, 'MySQL Replication is ONLINE');


import sys
import subprocess
import shlex


def mysql_repchk(arg):
    proc = subprocess.Popen(shlex.split(arg),
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            shell=False)

    out, err = proc.communicate()
    ret = proc.returncode
    return ret, out, err

RETCODE, OUTPUT, ERR = mysql_repchk('/usr/bin/mysql \
        --defaults-file=/root/.my.cnf \
        -e "SHOW SLAVE STATUS\\G"')

if RETCODE:
    print >> sys.stderr, "There was an error (%d): \n" % RETCODE
    print >> sys.stderr, ERR

if OUTPUT != "":
    SHOW_STATUS_LIST = OUTPUT.split('\n')
    del SHOW_STATUS_LIST[0]
    del SHOW_STATUS_LIST[-1]

    SLAVE_STATUS = {}
    for i in SHOW_STATUS_LIST:
        SLAVE_STATUS[i.split(':')[0].strip()] = i.split(':')[1].strip()

    if SLAVE_STATUS["Slave_IO_Running"] == "Yes" and \
            SLAVE_STATUS["Slave_SQL_Running"] == "Yes" and \
            SLAVE_STATUS["Last_Errno"] == "0":

        print "metric SLAVE_STATUS string ONLINE\n" \
            "metric SECONDS_BEHIND_MASTER int " \
            + SLAVE_STATUS["Seconds_Behind_Master"]
    else:
        print "metric SLAVE_STATUS string OFFLINE\n" \
            "metric SECONDS_BEHIND_MASTER int " \
            + SLAVE_STATUS["Seconds_Behind_Master"]

else:
    print "metric SLAVE_STATUS string NOT_CONFIGURED"
