#!/bin/bash

# dns-resolve.sh
# Rackspace Cloud Monitoring Plugin to verify the current return status of DNS lookups.
#
# Copyright (c) 2014, Lindsey Anderson <lindsey.anderson@rackspace.com>
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
# Example criteria:
#
#if (metric['dns_lookup'] != 'successful'){
#    return new AlarmStatus(CRITICAL, 'DNS Lookups are unavailable.');
#}
#return new AlarmStatus(OK, 'DNS Lookups from this server are responsive.');


RESOLVE_A="example.com"
dig ${RESOLVE_A} > /dev/null

if [[ $? -eq 9 || $? -eq 10 ]]; then
    echo "status critical dns_lookup unsuccessful"
    echo "metric dns_lookup string failed"
else
    echo "status ok dns_lookup successful"
    echo "metric dns_lookup string successful"
fi
