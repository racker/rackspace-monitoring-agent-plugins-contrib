#! /usr/bin/python
#
# Rackspace Cloud Monitoring Plug-In
# Check the status of a cassandra nodering and make sure none of the nodes
# have a '?' as a status.
#
# (c) 2017 Jim Wang <jim.wang@rackspace.com>
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
# It accepts three arguments, the path to the nodetool executable, the cassandra hostname
# and the port on which to run on
#
# Returns 1 status:
#   ok if the nodes don't have a '?' as a status
#   critical if the nodes has a '?' as a status
#

from subprocess import check_output
import sys
import argparse
parser = argparse.ArgumentParser(description='Run nodetool to check for inconsistent state')
parser.add_argument('-p', '--port', dest='portforcassandra',
                    default='9080', help='port that cassandra is running on')
parser.add_argument('-t', '--tool', dest='pathtonodetool',
                    default='/opt/cassandra/bin/',
                    help='path to nodetool executable (ex /opt/cassandra/bin/)')
parser.add_argument('-o', '--host', dest='cassandrahost',
                    default='localhost', help='host cassandra is running on.')
args = parser.parse_args()



try:
  nodetooloutput = check_output([args.pathtonodetool + '/nodetool', '-h',
                                 args.cassandrahost, '-p', args.portforcassandra, 'ring'])
  if nodetooloutput.find('?') >= 0:
    print 'status critical nodering not consistent, find out which nodes have the "?" status'
    sys.exit(2)
  else:
    print 'status ok nodering consistent'.exit(0)

except:
  print 'status critical nodering command failed'
  sys.exit(2)
