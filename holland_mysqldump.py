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
# Description:
# Monitors backup configs which use the mysqldump Holland plugin.
#
# Also monitors the dump file taken by Holland and the Holland logs.
#
# Requirements:
# Python 2.4 or greater
#
# Usage:
# Place script in /usr/lib/rackspace-monitoring-agent/plugins
# Ensure file is executable (755)
#
# Example Criteria
# if (metric['dump_age'] > 172800) {
#   return new AlarmStatus(CRITICAL, 'holland-plugin: mysqldump file is older \
#            than 2d.');
# }
# if (metric['error_count'] > 0) {
#   return new AlarmStatus(CRITICAL, 'holland-plugin: #{last_error}.');
# }
#
# return new AlarmStatus(OK, 'holland-plugin: Holland OK');

import os
import sys
import re
import time


def get_conf_value(config_file, key):
    try:
        config = open(config_file, 'r')
        for line in config.readlines():
            if line.startswith(key):
                    return line.split('=')[1].strip()
    except:
        print "status error unable to read %s" % config_file
        sys.exit(1)
    else:
        config.close()

    return None


class Holland:
    def __init__(self, backupset):
        self.config_file = '/etc/holland/holland.conf'
        self.backupset = backupset
        self.directory = get_conf_value(self.config_file, 'backup_directory')
        self.log = get_conf_value(self.config_file, 'filename')

        if not self.directory:
            print "status error cannot set holland backup directory location"
            sys.exit(1)
        elif not self.log:
            print "status error cannot set holland log file location"
            sys.exit(1)

    def get_log_mod_time(self):
        try:
            return int(os.path.getmtime(self.log))
        except OSError:
            print "status error unable to retrieve log file modified time"
            sys.exit(1)

    def get_log_position(self):
        try:
            return int(os.path.getsize(self.log))
        except OSError:
            print "status error unable to retrieve log file modified time"
            sys.exit(1)

    def get_time_since_dump(self):
        dump = os.path.join(self.directory, self.backupset, 'newest')
        try:
            current_time = time.time()
            return int(current_time - os.path.getmtime(dump))
        except OSError:
            print "status error unable to retrieve dump file modified time"
            sys.exit(1)

    def get_log_file(self):
        return self.log


class MySQL:
    def __init__(self, backupset):
        self.config_file = "/etc/holland/providers/mysqldump.conf"
        self.backupset_config = "/etc/holland/backupsets/%s.conf" % backupset


if __name__ == '__main__':
    if len(sys.argv) > 1:
        backupset = sys.argv[1]
    else:
        backupset = 'default'

    name = 'zzz_holland_backup_'+backupset

    holland = Holland(backupset)
    log_file = holland.get_log_file()
    log_modified = holland.get_log_mod_time()
    log_age = int(time.time() - log_modified)
    dump_age = holland.get_time_since_dump()
    log_pos = holland.get_log_position()

    match = '\[ERROR\]'
    split = '[ERROR]'
    exclude = 'Warning: Skipping the data of table mysql.event'

    # used to ensure we only read the newest lines and not the full log
    if os.access('/run/shm/', os.W_OK):
        tracking_file = '/run/shm/'+name
    elif os.access('/dev/shm/', os.W_OK):
        tracking_file = '/dev/shm/'+name
    else:
        print "status error failed to create tracking file"
        sys.exit(1)

    # check file is accessible
    if not os.access(log_file, os.R_OK):
        print "status error unable to access file", log_file
        sys.exit(1)

    # read info from tracking file
    if os.access(tracking_file, os.F_OK):
        try:
            tracking = open(tracking_file, 'r')
            contents = tracking.readline().rstrip('\n').split(',')
            prev_date = int(contents[0])
            prev_from = int(contents[1])
            prev_to = int(contents[2])
            if log_modified > prev_date:
                read_from_pos = prev_to
            else:
                read_from_pos = prev_from

            # account for log rotate
            if prev_to > log_pos:
                read_from_pos = 0
        except (ValueError, IndexError):
            read_from_pos = 0
            prev_date = 0
            tracking.close()
        except:
            print "status error unable to read tracking file"
            sys.exit(1)
        else:
            tracking.close()
    else:
        read_from_pos = 0
        prev_date = 0

    # find lines that match provided regex
    matched_lines = []
    reasons = []
    try:
        log = open(log_file, 'r')
        log.seek(read_from_pos)
        for line in log.readlines():
            if re.search(match, line) and not re.search(exclude, line):
                matched_lines.append(line)
                reasons.append(line.split(split)[1].strip())
    except:
        print "status error unable to read log file"
        sys.exit(1)
    else:
        log.close()

    # Get first and last error messages
    if len(reasons) > 0:
        first_error = reasons[0]
        last_error = reasons[-1]
    else:
        first_error = "none"
        last_error = "none"

    # write new tracking file - wait until after log has been read in case
    # of other issues
    if log_modified > prev_date:
        try:
            tracking = open(tracking_file, 'w')
            tracking.write(str(log_modified)+','+str(read_from_pos) + ',' +
                           str(log_pos))
        except:
            print "status error unable to write to tracking file"
            sys.exit(1)
        else:
            tracking.close()

    # Finally check SQL
    sql = MySQL(backupset)

    print "status success holland checked"
    print "metric log_age int64", log_age
    print "metric dump_age int64", dump_age
    print "metric error_count int64", len(matched_lines)
    print "metric first_error string", first_error
    print "metric last_error string", last_error
