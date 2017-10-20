#!/bin/env bash

# uptime_reset_detector.sh v 0.1.0a
# This script uses /dev/shm (volatile ramdisk )to detect reboots.
# Only works on Linux.
#
# Rackspace Cloud Monitoring Plugin to detect uptime resets.
#
# Copyright (c) 2017, Brian King <brian.king@rackspace.com>
# All rights reserved.
#
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

# Example criteria:
#
# if (metric['uptime_reset_detected'] == 'true'){
#    return new AlarmStatus(CRITICAL, 'Uptime reset detected.');
# }
# return new AlarmStatus(OK, 'Server has not rebooted since the last time we checked.');


if [ -e  /dev/shm/.lastreboot ]; then

    echo "status ok uptime_reset_detected false"
    echo "metric uptime_reset_detected string false just_rebooted"
    
    exit 0

    else
    
    echo "status critical uptime_reset_detected true"
    echo "metric uptime_reset_detected string true just_rebooted"
    
#We're not doing anything but checking for the presence of the file yet, but
# future versions could capture and report the delta between reboots 

    uptime -s > /dev/shm/.lastreboot
    
    exit 1

fi