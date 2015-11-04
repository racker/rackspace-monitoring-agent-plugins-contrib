#!/bin/bash

# nfs-status.sh
# Rackspace Cloud Monitoring Plugin to verify the current return status of nfs.
#
# Copyright (c) 2015, Philip Eatherington <philip.eatherington@rackspace.com>
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
# Verify the current status of NFS shares
#
# Example criteria :
#
# if (metric['nfs_status'] != 'ok') {
#   return new AlarmStatus(CRITICAL, 'NFS Service is NOT healthy.');
# }
#
# return new AlarmStatus(OK, 'NFS Service is running.');
#
# REQUIRES 'showmount' to be installed (part of NFS utils)

HOST=$1
DIR=$2

OUTPUT=$(showmount -e ${HOST} 2>&1)
if [[ $OUTPUT = *'Connection refused'* ]]
then
   state='Error: connection refused '
   error=$OUTPUT
elif [[ $OUTPUT = *'Program not registered'* ]]
then
   state='Error: NFS not running on host'
   error=$OUTPUT
elif [[ $OUTPUT = *$DIR* ]]
then
   state='ok'
   error='ok'
else
   state='Error: No shares found'
   error=$OUTPUT
fi
echo 'status' $state
echo 'metric nfs_status string' $error 
