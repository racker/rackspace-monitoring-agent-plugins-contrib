#! /usr/bin/python
#
# Rackspace Cloud Monitoring Plug-In
# Checks the number of compactions pending in a cassandra node.
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
# Returns the number of pending compactions on the cass node
#
#! /usr/bin/python

from subprocess import check_output
import sys
import string
import argparse

parser = argparse.ArgumentParser(description='Run nodetool to check for inconsistent state')
parser.add_argument('-p', '--port', dest='portforcassandra', default='9080', help='port that cassandra is running on')
parser.add_argument('-t', '--tool', dest='pathtonodetool', default='/opt/cassandra/bin/', help='path to nodetool executable (ex /opt/cassandra/bin)')
parser.add_argument('-o', '--host', dest='cassandrahost', default='localhost', help='host cassandra is running on.')

args = parser.parse_args();


node_tool_output = check_output([args.pathtonodetool + 'nodetool', '-h',
                                 args.cassandrahost, '-p', args.portforcassandra, 'compactionstats'])
pending_compactions = int(node_tool_output.splitlines()[0].split(':')[1])
print 'metric pending_compactions uint32 ' + str(pending_compactions)
