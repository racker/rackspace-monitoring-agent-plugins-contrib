#!/usr/bin/python
#
# Rackspace Cloud Monitoring Plugin to read HDFS metrics.
#
# USAGE;
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
# and run like this:
#
# hadoop_jobtracker.py [OPTIONS]
#
# OPTIONS
#   -n host   Set the namenode host (REQUIRED)
#   -p port   Set the namenode port
#   -u user   Set the Hadoop HDFS user name envariable.
#
#
# Requires: Python 2.7+
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
#
# if (metric['dead_nodes'] > 0) {
#   return new AlarmStatus(CRITICAL, 'Map-Reduce has #{dead_nodes} dead nodes');
# }
#
# if (metric['dead_nodes'] > 2) {
#   return new AlarmStatus(CRITICAL, 'Map-Reduce has #{dead_nodes} dead nodes');
# }
#
# return new AlarmStatus(OK, 'Map-Reduce Job Tracker OK');
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

import json
import os
import re
import sys

# 2.7+
import argparse

import urllib2


# Constants

# All types are uint32
METRIC_TYPE = 'uint32'

METRIC_NAMES = [
  'reduce_slots',
  'map_slots_used',
  'total_nodes',
  'dead_nodes',
  'map_slots',
  'alive_nodes',
  'reduce_slots_used'
]


def get_namenode_bean_data(namenode_host, namenode_port = 50030):
    """ Get the namenode bean data for namenode """

    # JMX URI for the hadoop namenode to get the JobTrackerInfo
    url = "http://{0}:{1}/jmx?qry=Hadoop%3Aservice%3DJobTracker%2Cname%3DJobTrackerInfo".format(namenode_host, namenode_port)

    beans = None
    try:
        response = urllib2.urlopen(url)
        content = response.read()
        data = json.loads(content)
        beans = data['beans'][0]
    except Exception, e:
        raise Exception("Error reading {0} url JSON - {1}".format(url, str(e)))

    return beans

def get_summary_metrics(d):
    """Get metrics for the AliveNodesInfoJson"""

    nodes_count = d['nodes']
    alive_count = d['alive']
    slots = d['slots']
    metrics = {
        'total_nodes' : nodes_count,
        'alive_nodes' : alive_count,
        'dead_nodes' : nodes_count - alive_count,
        'map_slots' : slots['map_slots'],
        'reduce_slots' : slots['reduce_slots'],
        'map_slots_used' : slots['map_slots_used'],
        'reduce_slots_used' : slots['reduce_slots_used']
    }

    return metrics


def get_job_tracker_metrics(beans):
    metrics = {}

    # Process the summary data
    summaryData = None
    summaryJson = beans.get('SummaryJson', None)
    if summaryJson is not None:
        summaryData = None
        try:
            summaryData = json.loads(summaryJson)
        except Exception, e:
            raise Exception("Error reading summary JSON - {0}: {1}".format(str(e), summaryJson))

        if summaryData is not None:
            m = get_summary_metrics(summaryData)
            metrics.update(m)

    if summaryData is None:
        raise Exception("No SummaryJson data in XML")
        return None

    return metrics


def main():
    """Main method"""

    parser = argparse.ArgumentParser(description='HDFS status metrics')
    parser.add_argument('-n', '--namenode',
                        default = None,
                        help = 'namenode host')
    parser.add_argument('-p', '--port',
                        default = 50030,
                        help = 'namenode port (Default 50030)')
    parser.add_argument('-u', '--user',
                        default = None,
                        help = 'user')

    args = parser.parse_args()

    ######################################################################

    user = args.user
    if user is not None:
        os.putenv("HADOOP_USER_NAME", user)
    namenode_host = args.namenode
    if namenode_host is None:
        print("Must give namenode host name")
        sys.exit(1)
    namenode_port = args.port

    try:
        beans = get_namenode_bean_data(namenode_host, namenode_port)
        if beans is None:
            sys.exit(1)

        metrics = get_job_tracker_metrics(beans)
        if metrics is None:
            sys.exit(1)

        print("status ok")
        for k, v in metrics.iteritems():
            print("metric {0} {1} {2}".format(k, METRIC_TYPE, v))
    except Exception, e:
        print("status err exception {0}".format(str(e)))

    sys.exit(0)

if __name__ == '__main__':
    main()
