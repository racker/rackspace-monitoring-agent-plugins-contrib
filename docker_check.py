#!/usr/bin/env python
"""Rackspace Cloud Monitoring Plugin for Docker."""

# Copyright 2015 Frank Ritchie <frank.ritchie@rackspace.com>
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
# This plugin monitors the Docker service via the 'docker info' command.
# By default the monitor fails if the check does not complete successfully.
# Metrics for:
#
# - the number of images
# - the number of containers
# - the number of go routines
# - the driver used
# - data space used
# - total data space
# - metadata space used
# - total metadata space
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
# docker_check.py -u <URL>
#
# The URL is optional and can be a TCP or Unix socket, e.g.
#
# docker_check.py -u tcp://0.0.0.0:2376
# or
# docker_check.py -u unix://var/run/docker.sock
#
# The default URL is unix://var/run/docker.sock.
#
# There is no need to define specific custom alert criteria.
# As stated, the monitor fails if the stats cannot be collected.
# It is possible to define custom alert criteria with the reported
# metrics if desired.
#

import sys
from docker import Client
from optparse import OptionParser


class DockerService(object):
    """Create on object for a Docker service. Assume it is stopped."""

    def __init__(self, url):

        self.url = url
        self.docker_running = False

    def docker_stats(self):
        """Connect to the Docker object and get stats. Error out on failure."""

        docker_conn = Client(base_url=self.url)

        try:
            docker_info = docker_conn.info()
            self.docker_running = True
        # Apologies for the broad exception, it just works here.
        except Exception:
            self.docker_running = False

        if self.docker_running:
            # Create a dict from the list of lists 'docker info' uses
            # to report Driver Status stats.
            driver_status = dict([(metric[0], metric[1]) for metric in \
                    docker_info['DriverStatus']])
             
            print 'metric images int64', docker_info['Images']
            print 'metric containers int64', docker_info['Containers']
            print 'metric go_routines int64', docker_info['NGoroutines']
            print 'metric driver string', docker_info['Driver']
            
            data_space_used_scalar, data_space_used_unit = \
                    driver_status['Data Space Used'].split()
            print 'metric data_space_used float', \
                   data_space_used_scalar, data_space_used_unit
            
            data_space_total_scalar, data_space_total_unit = \
                    driver_status['Data Space Total'].split()
            print 'metric data_space_total float', \
                   data_space_total_scalar, data_space_total_unit
            
            metadata_space_used_scalar, metadata_space_used_unit = \
                    driver_status['Metadata Space Used'].split()
            print 'metric metadata_space_used float', \
                   metadata_space_used_scalar, metadata_space_used_unit
            
            metadata_space_total_scalar, metadata_space_total_unit = \
                    driver_status['Metadata Space Total'].split()
            print 'metric metadata_space_total float', \
                   metadata_space_total_scalar, metadata_space_total_unit
            
            print 'status ok succeeded in obtaining docker stats.'
        else:
            print 'status err failed to obtain docker stats.'
            sys.exit(1)


def main():
    """Instantiate a DockerService object and collect stats."""

    parser = OptionParser()
    parser.add_option('-u', '--url', default='unix://var/run/docker.sock',
                      help='URL for Docker service (Unix or TCP socket).')
    (opts, args) = parser.parse_args()

    docker_service = DockerService(opts.url)
    docker_service.docker_stats()

if __name__ == '__main__':
    main()
