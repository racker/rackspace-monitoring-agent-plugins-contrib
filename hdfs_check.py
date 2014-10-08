#!/usr/bin/python
#
# Rackspace Cloud Monitoring Plugin to read HDFS metrics.
#
# USAGE;
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
# and run like this:
#
# hdfs_check.py [OPTIONS]
#
# OPTIONS
#   -H PATH   Pass in the hadoop binary path
#   -u user   Set the Hadoop HDFS user name envariable.
#
# Requires: Python 2.7+
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
#
# if (metric['datanodes_dead'] > 0) {
#   return new AlarmStatus(CRITICAL, 'HDFS has #{datanodes_dead} dead datanodes');
# }
#
# if (metric['datanodes_dead'] > 2) {
#   return new AlarmStatus(CRITICAL, 'HDFS has #{datanodes_dead} dead datanodes');
# }
#
# if (metric['blocks_missing'] > 0) {
#   return new AlarmStatus(CRITICAL, 'HDFS has #{blocks_missing} missing blocks');
# }
#
# if (metric['free_percent'] < 20) {
#   return new AlarmStatus(WARNING, 'HDFS has #{free_percent} free');
# }
#
# if (metric['free_percent'] < 10) {
#   return new AlarmStatus(CRITICAL, 'HDFS has #{free_percent} free');
# }
#
# return new AlarmStatus(OK, 'HDFS OK');
#
#
# Copyright (c) 2014, Dave Beckett <dave.beckett@rackspace.com>
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

from __future__ import print_function

import os
import re
import sys
import subprocess

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

# 2.7+
import argparse


HADOOP='/usr/bin/hadoop';

# Constants

METRIC_CONFIG = {
    # Bytes
    'total' : (None, 'uint64'), # calculated below
    'total_configured' : (re.compile(r'Configured Capacity: (\d+)'), 'uint64'),
    'total_present' : (re.compile(r'Present Capacity: (\d+)'), 'uint64'),
    'free' : (re.compile(r'DFS Remaining: (\d+)'), 'uint64'),
    'free_percent' : (None, 'double'), # calculated below
    'used' : (re.compile(r'DFS Used: (\d+)'), 'uint64'),
    'used_percent' : (re.compile(r'DFS Used%: (\d+)'), 'double'),

    # Blocks
    'blocks_under_replicated' : (re.compile(r'Under replicated blocks: (\d+)'), 'uint64'),
    'blocks_missing' : (re.compile(r'Missing blocks: (\d+)'), 'uint64'),
    'blocks_with_corrupt_replicas' : (re.compile(r'Blocks with corrupt replicas: (\d+)'), 'uint64'),

    # Datanodes
    # These 4 are not calculated yet; they need datanode blocks parsing
    'used_non_dfs' : (None, 'uint64'),
    'used_non_dfs_percent' : (None, 'double'),
    'datanode_remaining_max' : (None, 'uint32'),
    'datanode_remaining_min' : (None, 'uint32'),

    'datanodes_available' : (re.compile(r'Datanodes available: (\d+)'), 'uint32'),
    'datanodes_dead' : (re.compile(r'Datanodes available: \d+ \(\d+ total, (\d+) dead'), 'uint32'),
    'datanodes_total' : (re.compile(r'Datanodes available: \d+ \((\d+) total'), 'uint32'),
}



def get_hdfs_status_metrics(hadoop):
    """ Get HDFS status metrics

    May throw a subprocess exception if the hadoop command fails.

    """

    # Call the hdfs CLI command to get basic status
    cmd = [hadoop, 'dfsadmin', '-report']
    metrics = {}
    try:
        # Py2.7+
        # result = subprocess.check_output(cmd, stdin=None, stderr=None)
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=DEVNULL).communicate()[0]
    except Exception, e:
        raise Exception("command {0} failed {1}".format(str(cmd), str(e)))

    for line in result.split('\n'):
        if line.startswith('Name: '):
            break
        for (k, v) in METRIC_CONFIG.iteritems():
            (regexp, type_str) = v
            if regexp is not None:
                matches = regexp.match(line)
                if matches is not None:
                    metrics[k] = (matches.group(1), type_str)

    # Calculate capacity
    if 'total_configured' in metrics:
        metrics['capacity'] = metrics['total_configured']

    # Calculate free_percent
    if 'free' in metrics and 'total_configured' in metrics:
        remaining = int(metrics['free'][0])
        capacity = int(metrics['total_configured'][0])
        v = "{0:.2f}".format(remaining * 100.0 / capacity)
        metrics['free_percent'] = (v, 'double')
    else:
        metrics['free_percent'] = None

    return metrics


def main():
    """Main method"""

    parser = argparse.ArgumentParser(description='HDFS status metrics')
    parser.add_argument('-H', '--hadoop',
                        default = HADOOP,
                        help = 'hadoop command (default: {0})'.format(HADOOP))
    parser.add_argument('-u', '--user',
                        default = None,
                        help = 'user')

    args = parser.parse_args()

    ######################################################################

    hadoop = args.hadoop
    user = args.user
    if user is not None:
        os.putenv("HADOOP_USER_NAME", user)

    try:
        metrics = get_hdfs_status_metrics(hadoop)
        print("status ok")
        for k, t in metrics.iteritems():
            if t is not None:
                (v, type_str) = t
                print("metric {0} {1} {2}".format(k, type_str, v))
    except Exception, e:
        print("status err exception {0}".format(str(e)))

    sys.exit(0)

if __name__ == '__main__':
    main()
