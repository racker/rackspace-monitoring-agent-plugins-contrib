<#
Rackspace Cloud Monitoring Plug-In
This is a plugin to gather Windows performance counters for use
in Rackspace Monitoring checks.

(c) 2018 Rackspace US, Inc <support@rackspace.com>

All Rights Reserved.
Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Usage:
Place plug-in in C:\Program Files\Rackspace Monitoring\plugins

It accepts a single argument which is the CounterPath as used in perfmon.
For example, this will gather all counters for the logical disk C:

   '\LogicalDisk(c:)\*'

This plugin returns a metric for each counter gathered where the metric
name is normalized into

   $object.$instance.$counter

For example:

    logicaldisk.c.pct_free_space
    logicaldisk.c.free_megabytes
    logicaldisk.c.current_disk_queue_length
    logicaldisk.c.pct_disk_time
    logicaldisk.c.avg_disk_queue_length
    logicaldisk.c.pct_disk_read_time
    logicaldisk.c.avg_disk_read_queue_length

#>

function CM-GetCounters($CounterPath) {
  $results = Get-Counter -Counter $CounterPath
  $results.CounterSamples | ForEach-Object {
    $path = $_.Path
    $val = $_.CookedValue
    $metric = ($path -replace '\\\\.*?\\','' -replace '%','pct' -replace '\\','.' -replace '/',' per ' -replace '\(','.' -replace '[):]','' -replace '\.\s+','_' -replace '\s+','_').ToLower() -replace '[^a-z0-9:\.]','_'
    Write-Output "metric $metric double $val"
  }
  Write-Output "status ok success"
}

if($args.Count -lt 1) {
    Write-Output "status err Missing required parameter: CounterPath"
    exit
}

CM-GetCounters $args[0]