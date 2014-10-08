#!/usr/bin/python
#
# HDFS metrics
#
# USAGE;
#
# hdfs_check.py [OPTIONS]
#
# OPTIOSN
#   -H PATH   Pass in the hadoop binary path
#   -u user   Set the Hadoop HDFS user name envariable.
#
# Requires: Python 2.7+
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
