#!/usr/bin/env python
"""
Copyright 2015 Rackspace

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
----

Rackspace cloud monitoring plugin for statsd metrics.

Requires a directory path to watch and a list of metrics to filter out and return data about.

E.g.
python statsd_metric_emitter.py /foo/bar metric1 metric2 ... metricn
"""

import os.path
import sys
import glob
import json

ck_metrics = []
filtered_metrics = []

def output_check_status(status, message):
    ck_metrics.append("status %s %s" % (status, message))

    if status is "err":
        print("status %s" % (status, message))
        sys.exit()

def output_metrics(metrics):
    """
    Outputs the parsed metrics to the agent.
    """
    # TODO these need to work for a few different types
    for metric_type in ("counters", "timers", "gauges"):
        metric = metrics.get(metric_type)
        if metric is None:
            continue
        for name, val in ((k, v) for k, v in metric.iteritems() if not k.startswith('statsd.')):
            if name in filtered_metrics:
                for k, v in val.iteritems():
                    ck_metric = "metric %s %s %f" % (name + '.' + k, 'float', v)
                    ck_metrics.append(ck_metric)

def parse_file(file_path, offset=0):
    """
    Opens a metrics file from statsd and parses its json.

    Returns the offset of what we last read so we can seek
    directly to it next time.
    """
    with open(file_path, 'rb') as fd:
        fd.seek(offset)
        data = fd.read()
        for line in data.split("\n"):
            if line:
                output_metrics(json.loads(line))

        return fd.tell()

def find_latest_flush(files):
    s = sorted(files)
    if len(s) is 0:
        return None
    currentFile = s.pop()
    for i in s:
        os.remove(i)
    return currentFile
        
def main():
    if len(sys.argv) < 2:
        print("status err: 500 Expected a watch directory as argument (quitting)")
        sys.exit(1)
    if len(sys.argv) < 3:
        print("status err: 500 At least one metric name is required for filtering (quitting)")
        sys.exit(2)
    watch_dir = sys.argv[1]
    for i in range(2, len(sys.argv)):
        filtered_metrics.append(sys.argv[i])
    files = glob.glob(os.path.join(watch_dir, '[0-9]*.json'))
    currentFile = find_latest_flush(files)
    if currentFile is None:
        output_check_status('err', '204 NO CONTENT')
    else:
        parse_file(currentFile)
        output_check_status('ok', '200 OK')
    print('\n'.join(ck_metrics))

if __name__ == "__main__":
    main()

