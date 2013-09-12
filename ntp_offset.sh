#!/bin/bash

# ntp_offset.sh
# Rackspace Cloud Monitoring Plugin to verify the time offset from ntp
#
# Copyright (c) 2013, Jordan Evans <jordan.evans@rackspace.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
#
# Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in the
# documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
#
#
# This plugin expects to find ntpq and awk in the environment
# it reports the average ntp offset from ntpq in milliseconds.
#
# Example criteria :
# if (metric['ntp_offset'] > 10000) {
#   return new AlarmStatus(CRITICAL, 'ntp offset is too high.');
# }
# return new AlarmStatus(OK, 'ntp offset is fine.');
#

NTPQ_BIN=$(which ntpq)
AWK_BIN=$(which awk)

average() {
  count=0
  sum=0
  for x in $1
  do
    sum=$(($sum + $x))
    count=$(($count + 1))
  done
  echo $(($sum / $count))
}

if [ -x $NTPQ_BIN ] && [ -x $AWK_BIN ]
  then
    OUTPUT=$($NTPQ_BIN -pn | $AWK_BIN '{ if ($9 ~ /[0-9]/) print $9};' | cut -f 1 -d '.')
    OUTPUT=${OUTPUT/-/}
    AVG=$(average $OUTPUT)
    echo "metric ntp_offset int $AVG"
    echo "status ok ntp_offset calculated and reported."
  else
    echo "status err ntpq or awk is not executable"
fi
