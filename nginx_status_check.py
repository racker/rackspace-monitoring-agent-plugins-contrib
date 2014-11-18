#!/usr/bin/env python

import re
import sys
import urllib2
from optparse import OptionParser

class NginxStatus(object):
    """Create an object for an Nginx Status URL. Assume it is not available."""

    def __init__(self, url):

        self.url = url
        self.ngix_status_available = False

    def nginx_status_metrics(self):
        """Connect to the Nginx Status URL object and get the stats. Error out on failure."""

        nginx_status_conn = urllib2.urlopen('http://127.0.0.1/nginx_status')

        try:
            nginx_status_data = nginx_status_conn.read()
            nginx_status_metrics = {}
            self.nginx_status_available = True
        except Exception:
            self.nginx_status_available = False

        if self.nginx_status_available:
            # Create a dict from the metric reported by /nginx_stats
            match1 = re.search(r'Active connections:\s+(\d+)', nginx_status_data)
            match2 = re.search(r'\s*(\d+)\s+(\d+)\s+(\d+)', nginx_status_data)
            match3 = re.search(r'Reading:\s*(\d+)\s*Writing:\s*(\d+)\s*'
                 'Waiting:\s*(\d+)', nginx_status_data)

            nginx_status_metrics['connections'] = int(match1.group(1))

            nginx_status_metrics['accepted'] = int(match2.group(1))
            nginx_status_metrics['handled'] = int(match2.group(2))
            nginx_status_metrics['requests'] = int(match2.group(3))

            nginx_status_metrics['reading'] = int(match3.group(1))
            nginx_status_metrics['writing'] = int(match3.group(2))
            nginx_status_metrics['waiting'] = int(match3.group(3))

            print 'metric active_connections int64', nginx_status_metrics['connections']
            print 'metric accepted_connections int64', nginx_status_metrics['accepted']
            print 'metric handled_connections int64', nginx_status_metrics['handled']
            print 'metric number_of_requests int64', nginx_status_metrics['requests']
            print 'metric connections_reading int64', nginx_status_metrics['reading']
            print 'metric connections_writing int64', nginx_status_metrics['writing']
            print 'metric connections_waiting int64', nginx_status_metrics['waiting']


            print 'status ok succeeded in obtaining nginx status metrics.'
        else:
            print 'status err failed to obtain nginx status metrics.'
            sys.exit(1)


def main():
    """Instantiate an NginxStatus object and collect stats."""

    parser = OptionParser()
    parser.add_option('-u', '--url', default='http://127.0.0.1/nginx_status',
                      help='URL for Nginx Status page.')
    (opts, args) = parser.parse_args()

    nginx_status = NginxStatus(opts.url)
    nginx_status.nginx_status_metrics()

if __name__ == '__main__':
    main()
