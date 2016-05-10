#!/usr/bin/env python

#  Copyright 2013 Rackspace
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
# Usage:
# Place script in /usr/lib/rackspace-monitoring-agent/plugins
# Ensure file is executable. 
#
# Example alarm criteria that alerts if total number of files increases:
# 
# if (previous(metric['files']) < metric['files']) {
#     return new AlarmStatus(CRITICAL, 'Number of files found is #{files}');
# }
# 
# When filtering is applied it will use the 'after date' and 'above size' stats,
# as apposed to before/below, if either the 'size' or 'date' option is specified.

# <-- BEGIN README -->

# Monitors a specific home directory and reports various metrics.

# Only tested on CentOS and Ubuntu.  Windows would likely have issues.

# - If no username or parent directory is specified it will default to the home directory of the current user (root).
# - If a username is specified, but no directory, it will default to /home/<user>
# - If a directory is specified, but no username, it will default to <dir>/<current_user>

# Optional parameters:

# "-n", "--name" - filename, excluding extension
# "-e", "--extension" - extension, including intiial period
# "-s", "--size" - file size, in KB
# "-d", "--date" - modified date, in epoch format
# "-u", "--user" - user's who directory to monitor
# "-p", "--parent-dir" - parent directory for home path
# "-o", "--owner" - file owner
# "--filter" - see below

# Available metrics:
# files - Total number of files in directory
# name - No. of files with specified name
# ext - No. of files with specified file extension
# owner - No. of files owned by the specified user
# above_size,below_size - No. of files greater than or smaller than specified file size (in KB)
# date_after,date_before,date_on - No. of files modified before, after, or on specified date (in epoch format)

# If --filters param is provided only the 'files' metric will be returned.  This will be the number of files that meet all conditions specified.  In the case of the size and date metrics, it will only take into account above_size and date_after.

# Example check:

# {
#     "label": "Plugin_1",
#     "type": "agent.plugin",
#     "timeout": "20",
#     "period": "30",
#     "details": {
#         "file": "dir_monitor.py",
#         "args": ["--user=rack", "--extension=.bash_profile","--owner=root","--size=15","--date=1367888749","--parent-dir=/home/","--name=test"]
# }

# Example alarm:

# if (previous(metric['files']) < metric['files']) {
#     return new AlarmStatus(CRITICAL, 'Number of files found is #{files}');
# }

# <-- END README -->

# Author: James Buchan <james.buchan@rackspace.com>

from optparse import OptionParser
import os
import sys
import pwd

def main():
    usage = "usage: %prog [options] arg"
    parser = OptionParser(usage)
    parser.add_option("-n", "--name",
                      action="store", type="string", dest="name", help="filename")
    parser.add_option("-e", "--extension",
                      action="store", type="string", dest="extension", help="include initial period")
    parser.add_option("-s", "--size",
                      action="store", type="float", dest="size", help="in KB")
    parser.add_option("-d", "--date",
                      action="store", type="float", dest="date", help="date modified, epoch format")
    parser.add_option("-u", "--user",
                      action="store", type="string", dest="user", help="defaults to current user")
    parser.add_option("-p", "--parent-dir",
                      action="store", type="string", dest="parent_dir", help="defaults to /home/")
    parser.add_option("-o", "--owner",
                      action="store", type="string", dest="owner", help="file owner")
    parser.add_option("--filter", action="store_true", dest="filtering",
                      help="returns files that meet all conditions.")

    (options, args) = parser.parse_args()

    return options.name, options.extension, options.size, options.date, options.user, \
           options.parent_dir, options.owner, options.filtering 


def get_current_user():
    ''' Return existing user based on environment stats '''
    for var in ('LOGNAME', 'USER', 'LNAME', 'USERNAME'):
        user = os.getenv(var)
        if user:
            return user
    return pwd.getpwuid(os.getuid())[0]

def format_dir(parent_dir):
    ''' Add starting and trailing slashes to directory string if not included '''
    if parent_dir[0] != '/':
        parent_dir = '/' + parent_dir
    if parent_dir[-1] != '/':
        parent_dir = parent_dir + '/'
    return parent_dir


class Files:
    def __init__(self, path):
        self.path = path
        self.files = self.__get_all_files()

    def __get_all_files(self):
        files = [os.path.join(self.path,f) for f in os.listdir(self.path) 
            if os.path.isfile(os.path.join(self.path,f))]
        return files    

    def filter_files(self,filters):
        for f in self.files[:]:
            if f not in filters:
                self.files.remove(f)
            
    def get_total_files(self):
        return len(self.files)

    def get_files_with_name(self, name):
        # wont work as expected for double extension, eg. .tar.gz
        names = [f for f in self.files 
            if os.path.splitext(os.path.basename(f))[0] == name]
        return names

    def get_files_with_ext(self, ext):
        # wont work as expected for double extension, eg. .tar.gz
        exts = [f for f in self.files if os.path.splitext(f)[1] == ext]
        return exts

    def get_size_stats(self, size):
        a_size = []
        b_size = []
        size_kb = size*1024
        
        for f in self.files:
            try:
                file_size = os.path.getsize(f)
            except OSError:
                print "status err unable to retrieve file sizes"
                raise    
            
            if file_size > size_kb:
                a_size.append(f)
            elif file_size < size_kb:
                b_size.append(f)

        return a_size,b_size

    def get_files_with_owner(self, owner):
        owns = [f for f in self.files if pwd.getpwuid(os.stat(f).st_uid)[0] == owner]
        return owns

    def get_date_stats(self, date):
        a_date = []
        b_date = []
        o_date = []
        
        for f in self.files:
            try:
                file_mod = os.path.getmtime(f)
            except OSError:
                print "status err unable to retrieve file modified times"
                raise
            if file_mod > date:
                a_date.append(f)
            elif file_mod < date:
                b_date.append(f)
            else:
                o_date.append(f)
            
        return a_date,b_date,o_date

if __name__ == '__main__':
    args = main()

    name = args[0]
    extension = args[1]
    size = args[2]
    date = args[3]
    user = args[4]
    parent_dir = args[5]
    owner = args[6]
    filtering = args[7]

    # Set defaults if parameters not provided.
    if not user and not parent_dir:
        if 'HOME' in os.environ:
            path = os.getenv('HOME')
        elif os.name == 'posix':
            path = os.path.expanduser("~")
        else:
            print "status err unable to set home path"
            sys.exit(1)

    elif not user:
        user = get_current_user()
        parent_dir = format_dir(parent_dir)
        path = parent_dir + user

    elif not parent_dir:
        parent_dir = '/home/'
        path = parent_dir + user
    
    else:
        parent_dir = format_dir(parent_dir)
        path = parent_dir + user
 
    if not os.access(path, os.F_OK):
        print "status err unable to access path",path
        sys.exit(1)

    files = Files(path) 
    
    # Set individual stats if no filtering.
    if not filtering:
        if name: name_count = len(files.get_files_with_name(name))
        if extension: ext_count = len(files.get_files_with_ext(extension))
        if owner: owner_count = len(files.get_files_with_owner(owner))
        if size: 
            size_stats = files.get_size_stats(size)
            above_size_count = len(size_stats[0])
            below_size_count = len(size_stats[1])
        if date: 
            date_stats = files.get_date_stats(date)
            after_date_count = len(date_stats[0])
            before_date_count = len(date_stats[1])
            on_date_count = len(date_stats[2])
    # Filter total files bases on conditions set.
    else:
        if name: 
            files.filter_files(files.get_files_with_name(name))
        if extension:
            files.filter_files(files.get_files_with_ext(extension))
        if size:
            files.filter_files(files.get_size_stats(size)[0])
        if owner:
            files.filter_files(files.get_files_with_owner(owner))
        if date:
            files.filter_files(files.get_date_stats(date)[0])

    total = files.get_total_files()

    print "status ok",total,"files found at",path
    print "metric files int64",total
    if not filtering:
        if name:
            print "metric name int64",name_count
        if extension:
            print "metric ext int64",ext_count
        if size:
            print "metric above_size int64",above_size_count
            print "metric below_size int64",below_size_count
        if owner:
            print "metric owner int64",owner_count
        if date:
            print "metric date_after int64",after_date_count
            print "metric date_before int64",before_date_count
            print "metric date_on int64",on_date_count
