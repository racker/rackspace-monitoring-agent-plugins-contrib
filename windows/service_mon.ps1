<#

Script to return status of a Windows service.

Teddy Schmitz <teddy.schmitz@rackspace.com>
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

Configuration:

You must supply the name of the service in the arguments section of the agent config.
For example to monitor the plug in play service your check config should look like this:

"details": {
    "args": [
          "Plug and Play"
            ], 
     "file": "service_mon.ps1"
}


Example alarm criteria:

if (metric['service_status'] != 'running') {
return new AlarmStatus(CRITICAL, 'Service is NOT running.');
}


#>


function FuncCheckService{
 param($ServiceName)
    try{
        $arrService = Get-Service -Name $ServiceName -ErrorAction Stop
        }
        catch [Microsoft.PowerShell.Commands.ServiceCommandException]
        {
            Write-Output "status err $ServiceName service not found"
            exit
        }
    if ($arrService.Status -ne "Running")
    {       
        Write-Output "metric service_status string notrunning"
        Write-Output "status ok found service"
    }
    if ($arrService.Status -eq "running")
    { 
        Write-Output "metric service_status string running"
        Write-Output "status ok found service"
    }
 }

if($args.Count -lt 1){
    Write-Output "status err no service specified"
    exit
}
FuncCheckService -ServiceName $args[0]