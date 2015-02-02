#!/usr/bin/env python

'''
Reports disk usage in inodes

Takes arguments:

    :arg: directory - Which directory to run statvfs on. Will run like
    `df`, where it gets the information for the filesystem containing
    the directory.

Returns:
```
status ok success
metric inodes_percent float 0.000151 percent
metric inodes_total uint64 976761536 inodes
metric inodes_avail uint64 976613949 inodes
```

Or will return:

```
status err Failed to check status of inodes
```
'''
# MIT/X Consortium License
#
# © 2015 William Giokas <1007380@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import os
import sys
import operator


def __get_inode_usage(statvfsdata):
    '''
    Gets the available inodes.
    Returns three values in a dictionary::

        {
            percent: percent used,
            total_inodes: total number of indoes,
            avail_inodes: number of inodes used,
        }
    '''
    avail = statvfsdata.f_ffree
    files = statvfsdata.f_files
    try:
        percent = 1 - operator.truediv(avail, files)
    except ZeroDivisionError:
        percent = 0
    return {
        'percent': percent,
        'total_inodes': files,
        'avail_inodes': avail,
    }


def __get_usage(fsdir):
    '''
    Get the disk usage for the ``fsdir``
    '''
    try:
        return True, __get_inode_usage(os.statvfs(fsdir))
    except FileNotFoundError:
        return (False,)


def __get_status(error):
    if error[0]:
        return 'ok success'
    else:
        return 'err Failed to check status of inodes'


def return_inodes(fsdir='/'):
    '''
    Returns the rackspace monitoring agent status information. Format::

        status STATUS MESSAGE
        metric METRICNAME UNIT VALUE [UNIT]
    '''
    usage = __get_usage(fsdir)

    status = 'status %s' % (__get_status(usage))

    if usage[0]:
        metrics = [
            'metric inodes_percent float %f percent' % (
                usage[1]['percent']),
            'metric inodes_total uint64 %d inodes' % (
                usage[1]['total_inodes']),
            'metric inodes_avail uint64 %d inodes' % (
                usage[1]['avail_inodes'])
        ]

    else:
        metrics = []

    return '\n'.join([status] + metrics)


if __name__ == '__main__':
    a = sys.argv
    try:
        fs = a[1]
    except IndexError:
        fs = '/'

    print(return_inodes(fsdir=fs))
