#!/usr/bin/python
"""
Rackspace Cloud Monitoring plugin for pending cassandra tpstats (uses nodetool tpstats)

Example:
$ ./cassandra_pending_tpstats.py 

Example alarm criteria:
if (metric['cassandra_pending_foo'] > 10) {
	return new AlarmStatus(CRITICAL, 'Over 10 pending connections, increase resources')
}

if (metric['cassandra_pending_foo'] < 5) {
	return new AlarmStatus(CRITICAL, 'Under 5 pending connections, decrease resources')
}

Copyright 2015 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import re
import socket
import subprocess

def camel_to_underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

def parse_tpstats(output):
    return re.compile(r'([A-Za-z_]+)\s+\d+\s+(\d+)').findall(output)


statsd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
hostname = socket.gethostname().replace(".", "_")

output, error = subprocess.Popen(['nodetool','tpstats'], stdout=subprocess.PIPE).communicate()

if not error:
    for pool_name, count in parse_tpstats(output):
        pool_name = camel_to_underscore(pool_name)

        print "status ok"
        print "metric cassandra_pending_{pool} int {count}".format(pool=pool_name, count=count)
else:
    print "status err"
