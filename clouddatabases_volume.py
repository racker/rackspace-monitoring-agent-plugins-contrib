import os
import sys

import argparse
import pyrax


def check_usage(instance_id, threshold, region):
    pyrax.set_credential_file(
        os.path.expanduser("~/.rackspace_cloud_credentials"))
    cdb = pyrax.connect_to_cloud_databases(region=region)

    matched_instance = None
    for instance in cdb.list():
        if instance.id == instance_id:
            matched_instance = instance
    if not matched_instance:
        print 'status error Unable to find instance', instance_id
        sys.exit(1)

    # For usage lookup
    matched_instance.get()
    database_size = matched_instance.volume['size']
    database_usage = matched_instance.volume['used']
    percentage_used = database_usage / database_size

    if percentage_used >= threshold:
        print 'status error usage over threshold'
    else:
        print 'status ok usage within threshold'

    print "metric database_GB_container_size float", database_size
    print "metric database_GB_used float", database_usage
    print "metric percentage_used float", percentage_used

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("instance", help="Cloud Database instance id")
    parser.add_argument("region", help="Cloud region, e.g. DFW or ORD")
    parser.add_argument("threshold", nargs='?', default=85.0, type=float,
                        help="Storage threshold to alert on")
    args = parser.parse_args()
    check_usage(args.instance, args.threshold, args.region)

