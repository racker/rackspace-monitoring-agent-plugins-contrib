#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin to provide mongodb statistics.

Requirement:
pymongo - http://api.mongodb.org/python/current/

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
try:
    from pymongo import MongoClient as Client
except ImportError:
    from pymongo import Connection as Client
from pymongo.errors import ConnectionFailure, AutoReconnect


def mongodb_stats(host, port):
    try:
        c = Client(host, port)
    except ConnectionFailure, AutoReconnect:
        return None
    else:
        return c.test.command("serverStatus")


def main():
    if len(sys.argv) != 3:
        print "Usage: %s <host> <port>" % sys.argv[0]
        sys.exit(0)

    host = sys.argv[1]
    port = int(sys.argv[2])

    s = mongodb_stats(host, port)

    if not s:
        print "status err unable to generate statistics"
        sys.exit(0)

    print "status ok mongodb statistics generated"
    print "metric uptime float", s['uptime']
    print "metric conn_available int", s['connections']['available']
    print "metric conn_current int", s['connections']['current']
    print "metric conn_percent float", float(s['connections']['current']
                                             / s['connections']['available'])
    print "metric mem_mapped int", s['mem']['mapped']
    print "metric index_hits int", s['indexCounters']['hits']
    print "metric index_misses int", s['indexCounters']['misses']
    try:
        print "metric index_percent int", float(s['indexCounters']['hits']
                                            / s['indexCounters']['accesses'])
    except ZeroDivisionError:
        print "metric index_percent int 0"
    if 'repl' in s:
        print "metric is_replicating string true"
        print "metric is_master string", s['repl']['ismaster']
        print "metric is_secondary string", s['repl']['secondary']
    else:
        print "metric is_replicating string false"

if __name__ == '__main__':
    main()
