#!/bin/bash
#
# Description: Custom plugin returns number of pending security and other
# updated on a Ubuntu based system.
# Author: Tomaz Muraus
# License: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

OUTPUT=$(/usr/lib/update-notifier/apt-check 2>&1)

if [ $? -ne 0 ]; then
    echo "Failed to retrieve a number of pending updates"
    exit 100
fi

PENDING_OTHER=$(echo "${OUTPUT}" | cut -d ";" -f 1)
PENDING_SECURITY=$(echo "${OUTPUT}" | cut -d ";" -f 2)
REBOOT_REQUIRED="no"

if [ -f "/var/run/reboot-required" ]; then
  REBOOT_REQUIRED="yes"
fi

if [ $((PENDING_OTHER+PENDING_SECURITY)) -gt 0 ]; then
  UPGRADABLE_PACKAGES=$(apt list --upgradable 2>/dev/null | grep -v Listing | awk -F'/' '{print $1}' | paste -sd ',' -)
fi

echo "status Pending updates: security ${PENDING_SECURITY}, other: ${PENDING_OTHER}"

echo "metric pending_security uint32 ${PENDING_SECURITY}"
echo "metric pending_other uint32 ${PENDING_OTHER}"
echo "metric reboot_required string ${REBOOT_REQUIRED}"
echo "metric upgradable_packages string ${UPGRADABLE_PACKAGES}"

exit 0