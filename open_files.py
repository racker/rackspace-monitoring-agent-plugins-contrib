#!/usr/bin/env python
#
# Copyright 2015 Brad Ison <brad.ison@rackspace.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Rackspace Cloud Monitoring agent plugin to count open files on Linux.

This check records the number of file handles in use on a Linux
system using the proc file system:

  https://www.kernel.org/doc/Documentation/sysctl/fs.txt

Example alarm criteria:

  if (metric['open_files'] > 65535) {
    return new AlarmStatus(CRITICAL, "Too many open files!");
  }

"""

import sys


PROC_FILE = "/proc/sys/fs/file-nr"


try:
    open_nr, free_nr, max = open(PROC_FILE).readline().split("\t")
    open_files = int(open_nr) - int(free_nr)
except Exception as e:
    print "status error {}".format(e)
    sys.exit(1)


print "status ok {} open files".format(open_files)
print "metric open_files uint32 {}".format(open_files)
