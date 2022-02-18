#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin to provide file content.

Example usage includes, but is not limited to, monitoring version of OS.

Copyright 2013 Steve Katen <steve.katen@rackspace.com>
Copyright 2022 Honza Maly <hkmaly@post.cz>

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""
import sys
import os
import time


def main():
    if len(sys.argv) != 3:
        print "Requires a full path to the target passed as an first argument, the format as second."
        print "Expected formats are string, float, int32 etc OR version,"
        print "which we do our best to convert to float in usefull way."
        sys.exit(0)

    path = sys.argv[1]
    if not os.path.exists(path):
        print "status err target does not exist"
        sys.exit(0)

    format = sys.argv[2]
    try:
        with open(path) as f:
            lines = f.readlines()
            print "status ok target exists"
            i = 0
            for l in lines:
                i += 1
                if format == 'version':
                    p = l.strip().split('.')
                    major = float(p.pop(0))
                    minor = 0
                    if p:
                        for j in reversed(p):
                            minor = minor + float(j)
                            minor = minor / 100
                    print "metric line%d double %0.10f" % (i, major + minor)
                else:
                    print "metric line%d %s %s" % (i, format, l.strip())
    except Exception, e:
        print "status err Exception discovered: {}".format(str(e))


if __name__ == '__main__':
    main()
