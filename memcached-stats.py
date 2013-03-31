#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin to provide memcached statistics.

Copyright 2013 Steve Katen <steve.katen@rackspace.com>

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
import sys, telnetlib, re

def memcached_stats(host,port):
        regex = re.compile(ur"STAT (.*) (.*)\r")
        client = telnetlib.Telnet(host,port)
        client.write("stats\n")
        return dict(regex.findall(client.read_until('END')))

def hit_percent(hits,misses):
        total = hits + misses
        if (total > 0):
                return int(100 * float(hits) / float(total))
        else:
                return 0

def fill_percent(used,total):
        return int(used / total)

if (len(sys.argv) == 3):
        host = sys.argv[1]
        port = sys.argv[2]
else:
        print "Requires an IP Address + hostname passed as arguments"
        sys.exit(0)

stats = memcached_stats(host,port)

if (stats):
        print "status ok memcached statistics generated"
        print "metric uptime int", stats['uptime']
        print "metric curr_connections int", stats['curr_connections']
        print "metric listen_disabled_num int", stats['listen_disabled_num']
        print "metric curr_items int", stats['curr_items']
        print "metric total_items int", stats['total_items']
        print "metric evictions int", stats['evictions']
        print "metric hit_percent int", hit_percent(int(stats['get_hits']),int(stats['get_misses']))
        print "metric fill_percent int", fill_percent(int(stats['bytes']),int(stats['limit_maxbytes']))
else:
        print "status error unable to obtain statistics"
