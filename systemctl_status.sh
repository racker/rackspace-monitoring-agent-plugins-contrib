#!/bin/bash
#
# Copyright (c) 2018 Shane F. Carr
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# # # # # # # #
#
# This check returns information on the health of systemctl services.
# For more information on systemctl status strings, see:
# https://www.freedesktop.org/software/systemd/man/systemctl.html#is-system-running
#
# Suggested alarm:
#
# if (metric['systemctl_status'] != "running" && metric['systemctl_status'] != "starting") {
#   return new AlarmStatus(CRITICAL, 'SystemCTL status is #{systemctl_status}! Details: #{systemctl_failed_units}');
# }
# return new AlarmStatus(OK, 'SystemCTL status is #{systemctl_status}');

STATE=$(systemctl is-system-running)
DETAILS=$(systemctl list-units --state=failed --no-legend --no-pager | tr '\n' ' ')

echo "status ok succeeded in obtaining metrics"
echo "metric systemctl_status string $STATE"
if [ -z "$DETAILS" ]; then
    echo "metric systemctl_failed_units string (no failed units)";
else
    echo "metric systemctl_failed_units string $DETAILS";
fi
