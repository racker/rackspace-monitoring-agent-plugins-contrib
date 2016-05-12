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
