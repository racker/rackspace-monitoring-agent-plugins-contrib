<#

Rackspace Cloud Monitoring Plug-In

This is a plugin to monitor ICMP round-trip times for hosts that are only
reachable by the server

----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<zoltan.ver@gmail.com> wrote this file.  As long as you retain this notice
you can do whatever you want with this stuff. If we meet some day, and you
think this stuff is worth it, you can buy me a beer in return.
----------------------------------------------------------------------------

Usage:

- Place plug-in into the folder C:\Program Files\Rackspace Monitoring\plugins
- Configure Custom Plugin type check in Rackspace Intelligence
  Specify only the script's name and the required parameter(s), e.g.:
  ping.ps1 192.168.0.1
- Configure an Alert (optional, see example below)

This plugin returns 4 metrics:
  - minimum, average, maximum: statistics returned by the Windows ping utility
  in the format "Minimum = 0ms, Maximum = 17ms, Average = 4ms"
  - lost_packets : the percentage of the packets lost out of the number of probes
  sent (specifiied by the second parameter of this function or the -n command paramter)

Example alert:

--- start copying after this line ---

if (metric['average'] >= 15) {
    return new AlarmStatus(CRITICAL, 'Average round-trip takes #{average}ms');
}
if (metric['lost_packets'] >= 30) {
    return new AlarmStatus(CRITICAL, 'Packet loss is #{lost_packets}%');
}
if (metric['legacy_state'] != "ok") {
    return new AlarmStatus(WARNING, 'Error: #{legacy_state}');
}
return new AlarmStatus(OK, 'All good');

--- stop copying before this line ---
#>

function CM-Ping {
 param($TargetHost, $count)
    $ping_command = "ping -n $count -w 30 $TargetHost"
    $lines = iex $ping_command | select-string "loss|average"
    Try {
        $stats_loss = $lines[0]
        $stats_ping = $lines[1]
        $loss_percent = "$stats_loss".split("(")[1].split("%")[0]
        $result_ping = Foreach ($metric in "$stats_ping".split(",")) { $metric.Replace("    Minimum = ", "").Replace(" Maximum = ", "").Replace(" Average = ", "").Replace("ms", "") }
        $ping_min = $result_ping[0]
        $ping_max = $result_ping[1]
        $ping_avg = $result_ping[2]
    }
    Catch {
        Write-Output "status err $TargetHost could not be reached"
        Break
    }
    if ( $lines )
    {
        Write-Output "metric minimum int32 $ping_min milliseconds"
        Write-Output "metric average int32 $ping_avg milliseconds"
        Write-Output "metric maximum int32 $ping_max milliseconds"
        Write-Output "metric lost_packets int32 $loss_percent percent"
        Write-Output "status ok host responds"
    }
    else
    {
        Write-Output "status err $TargetHost could not be reached"
    }
 }

if($args.Count -lt 1){
    Write-Output "status err no host specified"
    exit
}

CM-Ping -TargetHost $args[0] 5
