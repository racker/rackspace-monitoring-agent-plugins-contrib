#!/usr/bin/env python
"""
Rackspace Cloud Monitoring plugin to provide file/directory information.

The three metrics returned for the target:
- age, calculated from ctime
- size, in bytes
- permissions, octal 

Copyright 2013 Steve Katen <steve.katen@rackspace.com> 

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
import sys, os, time

def mode(mode):
	return mode & 0777

if (len(sys.argv) == 2):
       	path = sys.argv[1]
else:
        print "Requires a full path to the target passed as an argument"
        sys.exit(0)

if (os.path.exists(path)):
	print "status ok target exists"

	details = os.stat(path)
	age = int(time.time() - details.st_ctime)
	size = int(details.st_size)
	mode = int(oct(mode(details.st_mode)))

	print "metric age int", age
	print "metric bytes int", size
	print "metric mode string", mode
else:
	print "status error target does not exist"

