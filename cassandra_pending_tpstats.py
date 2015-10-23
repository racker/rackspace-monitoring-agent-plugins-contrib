#!/usr/bin/python

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

        print "metric cassandra_pending_{pool} int {count}".format(pool=pool_name, count=count)
