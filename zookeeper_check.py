#!/usr/bin/env python
# License: MIT
# Author: Tomaz Muraus
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import socket

METRICS_TYPES_MAP = {
    'zk_version': 'string',
    'zk_avg_latency': 'uint32',
    'zk_max_latency': 'uint32',
    'zk_min_latency': 'uint32',
    'zk_packets_sent': 'gauge',
    'zk_packets_received': 'gauge',
    'zk_num_alive_connections': 'uint32',
    'zk_outstanding_requests': 'uint32',
    'zk_server_state': 'string',
    'zk_znode_count': 'uint32',
    'zk_watch_count': 'uint32',
    'zk_approximate_data_size': 'uint32',
    'zk_open_file_descriptor_count': 'uint32',
    'zk_max_file_descriptor_count': 'uint32',
    'zk_followers': 'uint32',
    'zk_synced_followers': 'uint32',
    'zk_pending_syncs': 'uint32',
    'zk_ephemerals_count': 'uint32'
}


def get_metrics(host='127.0.0.1', port=2181, timeout=5):
    sock = socket.socket()
    sock.settimeout(timeout)

    try:
        sock.connect((host, int(port)))
        sock.send('mntr')
        data = sock.recv(8192)
    except socket.error, e:
        print 'status Failed to connect: %s' % (str(e))
        sys.exit(1)
    finally:
        sock.close()

    metrics = parse_response(data)
    return metrics


def parse_response(data):
    metrics = {}

    for line in data.split('\n'):
        split = line.split('\t')

        if len(split) != 2:
            continue

        name, value = split[0], split[1]
        metrics[name] = value
    return metrics


def print_metrics(metrics):
    print 'status ZooKeeper v%s is running' % (metrics['zk_version'])

    for name, value in metrics.iteritems():
        metric_type = METRICS_TYPES_MAP[name]
        print 'metric %s %s %s' % (name, metric_type, value)


def main():
    if len(sys.argv) < 3:
        print 'Usage: zookeeper_check.py <host> <port> [timeout]'
        sys.exit(100)

    host = sys.argv[1]
    port = int(sys.argv[2])

    if len(sys.argv) == 4:
        timeout = int(sys.argv[3])
    else:
        timeout = None

    metrics = get_metrics(host=host, port=port)
    print_metrics(metrics)

main()
