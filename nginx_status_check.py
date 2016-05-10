#!/usr/bin/env python
"""Rackspace Cloud Monitoring Plugin for Nginx Status Page."""
# Copyright 2014 Frank Ritchie <frank.ritchie@rackspace.com>
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
# This plugin monitors the metrics produced by the Nginx ngx_http_stub_status_module
# module. The module generates an HTML page that contains basic status information.
#
# For more info see:
#
# http://nginx.org/en/docs/http/ngx_http_stub_status_module.html
#
# For advanced metrics the NGINX Plus product is required.
#
# By default the monitor fails if the check does not complete successfully.
#
# Metrics for:
#
# - Active connections
# - Accepted connections
# - Handled connections
# - Number of requests
# - Connections reading
# - Connections writing
# - Connections waiting
#
# are also reported.
#
# Requires:
# Python 2.6 or greater
# Nginx with ngx_http_stub_status_module enabled.
#
# In short, you will need to add a localtion block to the Nginx
# server block, e.g.
#
# location /nginx_status {
#     stub_status on;
#     access_log off;
#     allow 127.0.0.1;
#     }
#
# Usage:
# Place script in /usr/lib/rackspace-monitoring-agent/plugins.
# Ensure file is executable (755).
#
# Set up a Cloud Monitoring Check of type agent.plugin to run
#
# nginx_status_check.py -u <URL>
#
# The URL is optional and defaults to:
#
# http://0.0.0.0/nginx_status
#
# There is no need to define specific custom alert criteria.
# As stated, the monitor fails if the metrics cannot be collected.
# It is possible to define custom alert criteria with the reported
# metrics if desired.
#

import re
import sys
import urllib2
from optparse import OptionParser

class NginxStatus(object):
    """Create an object for an Nginx Status URL. Assume URL is not available."""

    def __init__(self, url):

        self.url = url
        self.nginx_status_available = False

    def nginx_status_metrics(self):
        """Connect to the Nginx Status URL object. Error out on failure."""

        try:
            nginx_status_conn = urllib2.urlopen(self.url)
            nginx_status_data = nginx_status_conn.read()
            self.nginx_status_available = True
        except urllib2.URLError:
            print 'status err URLError: check the URL and that Nginx running.'
            sys.exit(1)
        except Exception:
            print 'status err failed to obtain nginx status metrics.'
            sys.exit(1)

        if self.nginx_status_available:
            # Use regexes to parse /nginx_stats.
            match1 = re.search(r'Active connections:\s+(\d+)', nginx_status_data)
            match2 = re.search(r'\s*(\d+)\s+(\d+)\s+(\d+)', nginx_status_data)
            match3 = re.search(r'Reading:\s*(\d+)\s*Writing:\s*(\d+)\s*'
                    'Waiting:\s*(\d+)', nginx_status_data)
            print 'metric active_connections int64', int(match1.group(1))
            print 'metric accepted_connections int64', int(match2.group(1))
            print 'metric handled_connections int64', int(match2.group(2))
            print 'metric number_of_requests int64', int(match2.group(3))
            print 'metric connections_reading int64', int(match3.group(1))
            print 'metric connections_writing int64', int(match3.group(2))
            print 'metric connections_waiting int64', int(match3.group(3))
            print 'status ok succeeded in obtaining nginx status metrics.'
        else:
            print 'status err failed to obtain nginx status metrics.'
            sys.exit(1)


def main():
    """Instantiate an NginxStatus object and collect stats."""

    parser = OptionParser()
    parser.add_option('-u', '--url', default='http://0.0.0.0/nginx_status',
                      help='URL for Nginx Status page.')
    (opts, args) = parser.parse_args()

    nginx_status = NginxStatus(opts.url)
    nginx_status.nginx_status_metrics()

if __name__ == '__main__':
    main()
