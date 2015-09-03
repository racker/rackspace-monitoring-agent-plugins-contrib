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
# Monitors MySQL to ensure the credentials specified for Holland will succeed.
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
# if (metric['sql_ping_succeeds'] == 'false') {
#  return new AlarmStatus(CRITICAL, 'holland-plugin: MySQL is not running.');
# }
# if (metric['sql_creds_exist'] == 'false') {
#   return new AlarmStatus(CRITICAL, 'holland-plugin: MySQL credentials file \
#            does not exist.');
# }
# if (metric['sql_status_succeeds'] == 'false') {
#   return new AlarmStatus(CRITICAL, 'holland-plugin: MySQL credentials do \
#            not authenticate.');
# }
# if (metric['dump_age'] > 172800) {
#   return new AlarmStatus(CRITICAL, 'holland-plugin: mysqldump file is older \
#            than 2d.');
# }
# if (metric['error_count'] > 0) {
#   return new AlarmStatus(CRITICAL, 'holland-plugin: #{last_error}.');
# }
#
# return new AlarmStatus(OK, 'holland-plugin: MySQL and Holland OK');

import os
import sys
import re
import time
import subprocess


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
    def __init__(self, backupsets, config_file='/etc/holland/holland.conf'):
        self.config_file = config_file
        self.backupsets = backupsets
        self.directory = get_conf_value(self.config_file, 'backup_directory')
        self.log = get_conf_value(self.config_file, 'filename')

        if self.directory is None:
            print "status error cannot set holland backup directory location"
            sys.exit(1)
        elif self.log is None:
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
        current_time = time.time()
        dump_ages = []
        for backupset in self.backupsets:
            dump = os.path.join(self.directory, backupset, 'newest')
            try:
                dump_ages.append(int(current_time - os.path.getmtime(dump)))
            except OSError:
                print "status error unable to retrieve " + \
                    backupset + " dump file modified time"
                sys.exit(1)
        return max(dump_ages)

    def get_log_file(self):
        return self.log


class MySQL:
    def __init__(self, backupset):
        self.config_file = "/etc/holland/providers/mysqldump.conf"
        self.backupset_config = "/etc/holland/backupsets/%s.conf" % backupset
        if get_conf_value(self.backupset_config, 'user'):
            self.user = get_conf_value(self.backupset_config, 'user')
            self.password = get_conf_value(
                self.backupset_config, 'password').strip('"\'')
            self.host = get_conf_value(self.backupset_config, 'host')
        else:
            self.user = get_conf_value(self.config_file, 'user')
            self.password = get_conf_value(
                self.config_file, 'password').strip('"\'')
            self.host = get_conf_value(self.config_file, 'host')

        self.creds_files = get_conf_value(self.backupset_config,
                                          'defaults-extra-file')
        if not self.creds_files:
            self.creds_files = get_conf_value(self.config_file,
                                              'defaults-extra-file')

    # return boolean True if credentials set
    def check_creds(self):
        if (self.user and self.password):
            return True
        elif self.creds_files:
            for f in self.creds_files.split(','):
                if os.access(f, os.F_OK):
                    return True
            return False
        else:
            return False

    # return boolean True if ping succeeds
    def check_ping(self):
        try:
            DEVNULL = open(os.devnull, 'wb')
            if self.host:
                ping = subprocess.call([
                    "/usr/bin/mysqladmin",
                    "-h", self.host,
                    "ping"],
                    stdout=DEVNULL,
                    stderr=DEVNULL)
            elif self.creds_files:
                for f in self.creds_files.split(','):
                    try:
                        ping = subprocess.call([
                            "/usr/bin/mysqladmin",
                            "--defaults-file="+f, "ping"],
                            stdout=DEVNULL,
                            stderr=DEVNULL)
                        if ping == 0:
                            break
                    except:
                        ping = 0
            else:
                ping = subprocess.call([
                    "/usr/bin/mysqladmin",
                    "ping"],
                    stdout=DEVNULL,
                    stderr=DEVNULL)
        except:
            return False
        else:
            DEVNULL.close()

        if ping == 0:
            return True
        else:
            return False

    # return boolean True if status succeeds
    def check_status(self):
        try:
            DEVNULL = open(os.devnull, 'wb')
            if self.user and self.password:
                if self.host is None:
                    status = subprocess.call([
                        "/usr/bin/mysqladmin",
                        "-u", self.user,
                        "-p"+self.password,
                        "status"],
                        stdout=DEVNULL,
                        stderr=DEVNULL)
                else:
                    status = subprocess.call([
                        "/usr/bin/mysqladmin",
                        "-h", self.host,
                        "-u", self.user,
                        "-p"+self.password,
                        "status"],
                        stdout=DEVNULL,
                        stderr=DEVNULL)
            elif self.creds_files:
                for f in self.creds_files.split(','):
                    try:
                        status = subprocess.call([
                            "/usr/bin/mysqladmin",
                            "--defaults-file="+f, "status"],
                            stdout=DEVNULL,
                            stderr=DEVNULL)
                        if status == 0:
                            break
                    except:
                        status = 0
            else:
                status = subprocess.call([
                    "/usr/bin/mysqladmin",
                    "status"],
                    stdout=DEVNULL,
                    stderr=DEVNULL)
        except:
            return False
        else:
            DEVNULL.close()

        if status == 0:
            return True
        else:
            return False

if __name__ == '__main__':

    main_config_file = '/etc/holland/holland.conf'
    if len(sys.argv) > 1:
        backupsets = [sys.argv[1]]
    else:
        try:
            backupsets = [item.strip() for item in get_conf_value(
                main_config_file, 'backupsets').split(',')]
        except AttributeError:
            print "status error cannot set holland backupset"
            sys.exit(1)

    backupsets_str = '-'.join(backupsets)
    name = 'zzz_holland_backup_'+backupsets_str

    holland = Holland(backupsets, main_config_file)

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
            tracking.write(str(log_modified)+','+str(read_from_pos)+','
                           +str(log_pos))
        except:
            print "status error unable to write to tracking file"
            sys.exit(1)
        else:
            tracking.close()

    # Finally check SQL
    mysql_check_creds = []
    mysql_check_ping = []
    mysql_check_status = []
    for backupset in backupsets:
        sql = MySQL(backupset)
        mysql_check_creds.append(sql.check_creds())
        mysql_check_ping.append(sql.check_ping())
        mysql_check_status.append(sql.check_status())

    print "status success holland checked"
    print "metric log_age int64", log_age
    print "metric dump_age int64", dump_age
    print "metric error_count int64", len(matched_lines)
    print "metric first_error string", first_error
    print "metric last_error string", last_error
    print "metric sql_creds_exist string", str(
        all(mysql_check_creds)).lower()
    print "metric sql_ping_succeeds string", str(
        all(mysql_check_ping)).lower()
    print "metric sql_status_succeeds string", str(
        all(mysql_check_status)).lower()
