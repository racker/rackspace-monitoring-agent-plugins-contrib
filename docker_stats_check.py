#!/usr/bin/env python
"""Rackspace Cloud Monitoring Plugin for Docker Stats."""

# Copyright 2015 Nachiket Torwekar <nachiket.torwekar@rackspace.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -----
#
# This plugin monitors the Docker containers via the 'docker stats' command.
# By default the monitor fails if the check does not complete successfully.
# Metrics for:
#
# - cpu_total_usage
# - cpu_system_usage
# - cpu_kernel_mode_usage
# - cpu_user_mode_usage
# - cpu_user_mode_usage
# - memory_max_usage
# - memory_total_cache
# - network_rx_bytes
# - network_rx_packets
# - network_tx_bytes
# - network_tx_packets
#
# are also reported.
#
# Requires:
# Python 2.6 or greater
# docker-py: https://github.com/docker/docker-py
#
# Usage:
# Place script in /usr/lib/rackspace-monitoring-agent/plugins.
# Ensure file is executable (755).
#
# Set up a Cloud Monitoring Check of type agent.plugin to run
#
# docker_stats_check.py -u <URL> -c <container>
#
# The URL is optional and can be a TCP or Unix socket, e.g.
#
# docker_stats_check.py -u tcp://0.0.0.0:2376
# or
# docker_stats_check.py -u unix://var/run/docker.sock
#
# The default URL is unix://var/run/docker.sock.
# 
# The container can be name or id
# docker_stats_check.py -u unix://var/run/docker.sock -c agitated_leakey
# or
# docker_stats_check.py -u unix://var/run/docker.sock -c 1f3b3b8f0fcc
#
# There is no need to define specific custom alert criteria.
# As stated, the monitor fails if the stats cannot be collected.
# It is possible to define custom alert criteria with the reported
# metrics if desired.
#

import sys
from docker import Client
from optparse import OptionParser
from subprocess import call
import json

class DockerService(object):
    """Create an object for a Docker service. Assume it is stopped."""

    def __init__(self, url, container):

        self.url = url
        self.container = container
        self.docker_running = False

    def docker_stats(self):
        """Connect to the Docker object and get stats. Error out on failure."""

        docker_conn = Client(base_url=self.url)

        try:
            stats = docker_conn.stats(self.container)
            self.docker_running = True
        # Apologies for the broad exception, it just works here.
        except Exception:
            self.docker_running = False

        if self.docker_running:
            print 'status ok succeeded in obtaining docker container stats.'
            for stat in stats:
                s = json.loads(stat)
                print 'metric cpu_total_usage int64', s['cpu_stats']['cpu_usage']['total_usage']
                print 'metric cpu_system_usage int64', s['cpu_stats']['system_cpu_usage']
                print 'metric cpu_kernel_mode_usage int64', s['cpu_stats']['cpu_usage']['usage_in_kernelmode']
                print 'metric cpu_user_mode_usage int64', s['cpu_stats']['cpu_usage']['usage_in_usermode']
                print 'metric memory_max_usage int64', s['memory_stats']['max_usage']
                print 'metric memory_total_cache int64', s['memory_stats']['stats']['total_cache']
                print 'metric network_rx_bytes int64', s['network']['rx_bytes']
                print 'metric network_rx_packets int64', s['network']['rx_packets']
                print 'metric network_tx_bytes int64', s['network']['tx_bytes']
                print 'metric network_tx_packets int64', s['network']['tx_packets']

        else:
            print 'status err failed to obtain docker container stats.'
            sys.exit(1)


def main():
    """Instantiate a DockerStats object and collect stats."""

    parser = OptionParser()
    parser.add_option('-u', '--url', default='unix://var/run/docker.sock',
                      help='URL for Docker service (Unix or TCP socket).')
    parser.add_option('-c', '--container',
                      help='Name or Id of container that you want to monitor')
    (opts, args) = parser.parse_args()
    if opts.container is None:
        parser.error("options -c is mandatory")

    docker_service = DockerService(opts.url, opts.container)
    docker_service.docker_stats()

if __name__ == '__main__':
    main()