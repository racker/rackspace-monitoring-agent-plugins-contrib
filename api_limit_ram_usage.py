#!/usr/bin/env python
'''Rackspace Cloud Servers RAM usage monitor'''

# Copyright 2013 Rackspace

# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.
import sys
import pyrax
import argparse


def main():
    '''Script execution'''
    parser = argparse.ArgumentParser(description='get percent of api limit '
                                                 'of ram used')
    parser.add_argument('-u', '--username', help='Rackspace Username',
                        required=True)
    parser.add_argument('-a', '--apikey', help='Rackspace API Key',
                        required=True)
    parser.add_argument('-m', '--maxthreshold',
                        help='API Percent Used Threshold, integer between '
                             '1-99',
                        required=True)
    parser.add_argument('--human',
                        help='Format output for humans, not Cloud Monitoring',
                        action='store_true')
    args = parser.parse_args()

    if int(args.maxthreshold) < 1 or int(args.maxthreshold) > 99:
        print "You must enter a valid integer from 1-99 for maxthreshold"
        sys.exit(2)
    pyrax.set_setting("identity_type", "rackspace")
    pyrax.set_credentials(args.username, args.apikey)

    (ram_used, ram_allowed) = getlimits()
    display_usage(ram_used, ram_allowed, args.maxthreshold, args.human)


def getlimits():
    '''Returns the RAM usage and limits'''
    compute = pyrax.cloudservers
    cslimits = compute.limits.get()
    # Convert the generator to a list
    cslimits_list = [rate for rate in cslimits.absolute]
    # Pull out max_ram api limit and total used ram from list
    max_ram = [
        x.value for x in cslimits_list if x.name == "maxTotalRAMSize"][0]
    total_ram = [x.value for x in cslimits_list if x.name == "totalRAMUsed"][0]
    return (total_ram, max_ram)


def display_usage(ram_used, ram_allowed, alert_percentage, human):
    '''Print RAM usage information'''
    percent_ram = (float(ram_used) / float(ram_allowed)) * 100
    percent_ram_used = round(float(("%.2f" % percent_ram)))

    if human:
        print "Current RAM Usage: %sMB" % ram_used
        print "Max RAM API Limit: %sMB" % ram_allowed
        if percent_ram_used >= float(alert_percentage):
            print "WARNING: Percent of API Limit Used: %d%%" % (
                percent_ram_used)
        else:
            print "OK: Percent of API Limit Used: %0d%%" % percent_ram_used
    else:
        # Cloud Monitoring-aware output
        if percent_ram_used < float(alert_percentage):
            print "status ok Percent RAM Used", percent_ram_used
            print "metric percent_ram_used float", percent_ram_used
        else:
            print "status err Percent RAM Used", percent_ram_used
            print "metric percent_ram_used float", percent_ram_used


if __name__ == "__main__":
    main()
