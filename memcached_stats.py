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
import sys
import telnetlib
import re
import socket


def memcached_stats(host, port):
    regex = re.compile(ur"STAT (.*) (.*)\r")
    try:
        c = telnetlib.Telnet(host, port)
    except socket.error:
        return
    else:
        c.write("stats\n")
        return dict(regex.findall(c.read_until('END')))


def hit_percent(hits, misses):
    total = hits + misses
    if total > 0:
        return 100 * float(hits) / float(total)
    else:
        return 0.0


def fill_percent(used, total):
    return 100 * float(used) / float(total)


def main():
    if len(sys.argv) != 3:
        print "Usage: %s <host> <port>" % sys.argv[0]
        sys.exit(0)

    host = sys.argv[1]
    port = sys.argv[2]
    s = memcached_stats(host, port)

    if not s:
        print "status err unable to generate statistics"
        sys.exit(0)

    print "status ok memcached statistics generated"
    print "metric uptime int", s['uptime']
    print "metric curr_connections int", s['curr_connections']
    print "metric listen_disabled_num int", s['listen_disabled_num']
    print "metric curr_items int", s['curr_items']
    print "metric total_items int", s['total_items']
    print "metric evictions int", s['evictions']
    print "metric hit_percent float", hit_percent(int(s['get_hits']),
                                                  int(s['get_misses']))
    print "metric fill_percent float", fill_percent(int(s['bytes']),
                                                    int(s['limit_maxbytes']))

if __name__ == '__main__':
    main()
