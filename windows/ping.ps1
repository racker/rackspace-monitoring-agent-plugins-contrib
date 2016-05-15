<#

Rackspace Cloud Monitoring Plug-In

This is a plugin to monitor ICMP response times of hosts accessible by the server

----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<zoltan.ver@gmail.com> wrote this file.  As long as you retain this notice you
can do whatever you want with this stuff. If we meet some day, and you think
this stuff is worth it, you can buy me a beer in return.
----------------------------------------------------------------------------

Usage:
- Place plug-in in folder C:\Program Files\Rackspace Monitoring\plugins
- Configure Custom Plugin type check in Rackspace Intelligence
  Specify only the script's name and the hostname/IP to ping, e.g.:
  ping.ps1 192.168.0.1 <count> <interval>
  Count is the amount of ICMP probes sent in a singe check, and interval is the
  number of seconds between them. They are both optional. Their default values
  are 5 pings with an interval of 2 seconds.
- Configure an Alert (optional, see example below).

This plugin returns 4 metrics:
  - minimum, average, maximum: statistics returned by the Windows ping utility
    in the format "Minimum = 0ms, Maximum = 17ms, Average = 4ms
  - lost_packets: the percentage of the packets lost out of the number of probes
    sent

Example alert:

--- start copying after this line ---

if (metric['average'] >= 30 ) {
    return new AlarmStatus(WARNING, 'Average round-trip took #{average}ms');
}
if (metric['lost_packets'] >= 40) {
    return new AlarmStatus(WARNING, 'Packet loss was #{lost_packets}%');
}
if (metric['legacy_state'] != "ok") {
    return new AlarmStatus(CRITICAL, 'Error: #{legacy_state}');
}
return new AlarmStatus(OK, 'All good');

--- stop copying before this line ---

#>

function CM-Ping($TargetHost, $count, $interval) {
    $ping_command = "ping -n 1 -w 30 $TargetHost"
    $lost_packets=0
    if (-not $count) { $count = 5 }
    if (-not $interval ) { $interval = 2 }
    [int[]] $ping_min, $ping_max, $ping_avg = @()
    for ($i=0; $i -lt $count; $i++) {
        $lines = iex $ping_command | select-string "loss|average"
        if (0 -eq $LASTEXITCODE) {
            $stats_loss = $lines[0]
            $stats_ping = $lines[1]
            if ([int]"$stats_loss".split("(")[1].split("%")[0] -gt 0) {
                $lost_packets++
            }
            $result_ping = Foreach ($metric in "$stats_ping".split(",")) { $metric.Replace("    Minimum = ", "").Replace(" Maximum = ", "").
Replace(" Average = ", "").Replace("ms", "") }
            $ping_min += [int]$result_ping[0]
            $ping_max += [int]$result_ping[1]
            $ping_avg += [int]$result_ping[2]
            sleep $interval
        }
        else {
            $lost_packets++
        }
    }
    if ( $lines ) {
        Write-Output "metric minimum int32 $(($ping_min | measure -Minimum).Minimum) milliseconds"
        Write-Output "metric average double $(($ping_min | measure -Average).Average) milliseconds"
        Write-Output "metric maximum int32 $(($ping_min | measure -Maximum).Maximum) milliseconds"
        Write-Output "metric lost_packets int32 $([int](([int]$lost_packets / [int]$count) * 100)) percent"
        Write-Output "status ok"
    }
    else {
        Write-Output "status err $TargetHost could not be reached"
    }
 }

if($args.Count -lt 1) {
    Write-Output "status err Missing required parameter"
    exit
}

CM-Ping -TargetHost $args[0] $args[1] $args[2]
