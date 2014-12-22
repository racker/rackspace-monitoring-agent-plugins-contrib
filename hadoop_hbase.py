#!/usr/bin/python
#
# Rackspace Cloud Monitoring Plugin to read HBase metrics.
#
# USAGE;
# Place plug-in in /usr/lib/rackspace-monitoring-agent/plugins
# and run like this:
#
# hadoop_hbase.py [OPTIONS]
#
# OPTIONS
#   -b PATH   Pass in the hbase binary path
#   -u user   Set the Hadoop HBase user name envariable.
#
# Requires: Python 2.6+   May work on Python 3+
#
# The following is an example 'criteria' for a Rackspace Monitoring Alarm:
#
#
# if (metric['dead_regionservers'] > 0) {
#   return new AlarmStatus(WARNING, 'HBase has #{dead_regionservers} dead region servers');
# }
#
# if (metric['dead_regionservers_percent'] > 20) {
#   return new AlarmStatus(CRITICAL, 'HBase has #{dead_regionservers_percent}% dead region servers');
# }
#
# return new AlarmStatus(OK, 'HBase OK');
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
from tempfile import NamedTemporaryFile

try:
    from subprocess import DEVNULL # py3k
except ImportError:
    import os
    DEVNULL = open(os.devnull, 'wb')

import argparse


HBASE='/usr/bin/hbase';

# Constants
ERROR_RE = re.compile('r^ERROR: (.+)')
LIVE_RE = re.compile(r'^(\d+) live servers')
DEAD_RE = re.compile(r'^(\d+) dead servers')
LOAD_RE = re.compile(r'^^Aggregate load: (\d+)')
REGIONS_RE = re.compile(r'^^Aggregate load: \d+, regions: (\d+)')


def get_hbase_status_metrics(hbase):
    """ Get HBase status metrics 

    :param hbase Path to 'hbase' command
    """

    f = None
    try:
        f = NamedTemporaryFile(delete=False)
        f.write("status 'simple'\nexit\n")
        f.close()
    except Exception, e:
        raise Exception("write to {0} failed {1}".format(f.name if f else "", str(e)))

    # Call the hbase CLI command to get basic status
    cmd = [hbase, 'shell', f.name]
    metrics = {}
    total_rs = 0
    try:
        # Py2.7+ adds check_output so the DEVNULL line can be removed
        # result = subprocess.check_output(cmd, stdin=None, stderr=None)
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=DEVNULL).communicate()[0]
        for line in result.split('\n'):
            matches = ERROR_RE.match(line)
            if matches is not None:
                raise Exception("hbase shell returned error {0}".format(matches.group(1)))

            matches = LIVE_RE.match(line)
            if matches is not None:
                v = int(matches.group(1))
                total_rs += v
                metrics['live_regionservers'] = (v, 'uint32')

            matches = DEAD_RE.match(line)
            if matches is not None:
                v = int(matches.group(1))
                total_rs += v
                metrics['dead_regionservers'] = (v, 'uint32')

            matches = LOAD_RE.match(line)
            if matches is not None:
                v = int(matches.group(1))
                metrics['aggregate_load'] = (v, 'uint32')

            matches = REGIONS_RE.match(line)
            if matches is not None:
                v = int(matches.group(1))
                metrics['regions'] = (v, 'uint32')

    except Exception, e:
        raise Exception("command {0} failed {1}".format(str(cmd), str(e)))
    finally:
        os.unlink(f.name)
    
    metrics['total_regionservers'] = (total_rs, 'uint32')

    for k in ['live_regionservers', 'dead_regionservers']:
        if k in metrics:
            v = "{0:.2f}".format(metrics[k][0] * 100.0 / total_rs)
            metrics[k + '_percent'] = (v, 'double')

    return metrics


def main():
    """Main method"""

    parser = argparse.ArgumentParser(description='HBase status metrics')
    parser.add_argument('-b', '--hbase',
                        default = HBASE,
                        help = 'hbase command (default: {0})'.format(HBASE))
    parser.add_argument('-u', '--user',
                        default = None,
                        help = 'user')

    args = parser.parse_args()

    ######################################################################

    hbase = args.hbase
    user = args.user
    if user is not None:
        os.putenv("HADOOP_USER_NAME", user)

    try:
        metrics = get_hbase_status_metrics(hbase)
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
