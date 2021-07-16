#!/usr/bin/env python3

'''
Copyright 2021 Teddy Belitsos teddy.belitsos@rackspace.com

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.


Usage And Setup:

Description:
Monitors for the success or failure of Rackspace Cloud Database backups 
via the Rackspace Cloud Database API. The design intent of this script is
to alert clients of failed manual or automatic backups of a Cloud Database.

Script Setup:
Place script in /usr/lib/rackspace-monitoring-agent/plugins.
Ensure the script has the execute privilegde chmod u+x.

Preface:
This monitoring script interacts directly with the Rackspace Cloud Databases 
public API. As such, this script requires a valid user and affilated apikey 
to interact with a given cloud account. As a precaution, DO NOT USE the username 
and apikey of any cloud account user that has admin priviledges to the account. 
Doing so runs the risk of a less priviledge user on the cloud account viewing 
the monitoring arguments in the Rackspace Inteliigence control panel which includes 
the username and apikey.

Requirements:
This script is designed to check the backup status of a scheduled Cloud Database 
backup via the Cloud Database API. The script must be run from a server that has 
the Rackspace Intelligence monitoring agent installed and linked to the Rackspace 
cloud account that the dbaas belongs to. 


Step #1: Create a Read Only API Cloud User:
To create a secure read only cloud account user, perform the following steps:

1.a Create a new cloud account user. The username does not matter to the script.

2.b Edit the user, go to Product Permissions and click edit. This will pull up 
   a list of all of the products said user has access to. To easily remove unneeded 
   permissions, set the Cloud Access to None at first to blank all permissions. Then 
   change Cloud Access to Custom and set the following permissions for the services:

Databases: Observer
Monitoring: Observer

All other permissions should be set to none.
Click update to apply the permissions to the user that was just created.


Step #2: Crafting The Monitoring Script Arguments
This script expects the following arguments to be passed at execution:
--instance-id INSTANCE_ID or --ha-id HA_ID 
--apikey APIKEY 
--username USERNAME 
--region REGION

To make configuration easier, it is recommend to stage the command line arguments in
a text editor first and then copy/paste into the Command Line box in RS Intelligence
when creating the monitoring check.

Example Script Arguments By Use Case:

-Monitoring HA Group Scheduled Backup: 
If you need to monitor for the completion of a scheduled backup for a High Availability
group, supply the HA Group uuid:
cloud_database_backup.py --ha-id HA_ID --apikey APIKEY --username USERNAME --region REGION

-Monitoring Standalone Instance Scheduled Backup:
If you need to monitor the backup status for a standalone instance, supply the
instance's uuid:
cloud_database_backup.py --instance-id INSTANCE_ID --apikey APIKEY --username USERNAME --region REGION


Step #3: Create The Custom Monitoring Check For The Desired Monitored Entity

Type: Custom
Check Name: name_the_check
Command: plugin_name + arguments (See example in Step #3)


Step #4: Write The Alarm Criteria - Example RS Intelligence Monitoring Criteria:

if (metric['backup_status'] != 'COMPLETED') {
    return new AlarmStatus(CRITICAL, 'The cloud database instance did not backup!.');
}
return new AlarmStatus(OK, 'The backup job executed on #{backup_date} named #{backup_name} has #{backup_status}.');

Alarm test result: OK, "The backup job executed on 2021-04-22T06:00:55Z named cdb-automated-backup-2021-04-22T06:00:50Z has COMPLETED."


Step #5: Test
At this point you've created a new cloud user that is read only and you're using said
user's username and apikey to authenticate against the Racksapce API to pull Cloud 
Database instance and backup information. This script has built in error checking and 
will notify you via STDOUT error messages should it encounter issues with incorrectly 
supplied arguments and or trouble interacting with the APIs. 
'''

import urllib3
import json
import sys
import argparse


def cli():
    description_string = ('Check if the most recent backup of a Rackspace Cloud Database was successful. You can specify a\
    stand alone instance_id or an ha_group_id')

    parser = argparse.ArgumentParser(description=description_string)

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--instance-id', type=str, help='The instance ID for a standalone cloud database.')
    group.add_argument('--ha-id', type=str, help='The HA group instance ID for a high availability cloud database cluster.')

    parser.add_argument('--apikey', type=str, required=True, help='API key for a Rackspace Cloud account.')
    parser.add_argument('--username', type=str, required=True, help='Username for a Rackspace Cloud account.')
    parser.add_argument('--region', type=str, required=True, help='Datacenter cloud database is located in: DFW, ORD, IAD, LONG, HKG.')

    args = parser.parse_args()

    # Calling main method with supplied arguments from argparse
    main(apikey=args.apikey, username=args.username, region=args.region, instance_id=args.instance_id, ha_group_id=args.ha_id)


def main(apikey, username, region, instance_id, ha_group_id):

    # These variables contain the account information necessarry to interact 
    # with a client's Rackspace Cloud API endpoint.
 
    # Grab auth_token and tenant_id    
    api_creds = api_authenticate(apikey, username)
    auth_token = api_creds[0] 
    tenant_id = api_creds[1]

    valid_dbaas = validate_instance_presence(tenant_id, region, instance_id, ha_group_id, auth_token)

    if valid_dbaas == True:
        backup_status = get_backups(tenant_id, region, instance_id, ha_group_id, auth_token)
    else:
        print('Error! Instance was not found. Please check the UUID for accuracy.')
        sys.exit(1)
   
    if 'COMPLETED' in backup_status:
        # Status Message
        print(f'status of most recent backup: {backup_status}')
        # Metric
        print(f'metric backup_status string {backup_status[0]}')
        print(f'metric backup_date string {backup_status[1]}')
        print(f'metric backup_name string {backup_status[2]}')
        sys.exit(0)
    elif 'FAILED' in backup_status:
        # Status Message
        print(f'status of most recent backup: {backup_status}')
        # Metric
        print(f'metric backup_status string {backup_status[0]}')
        print(f'metric backup_date string {backup_status[1]}')
        print(f'metric backup_name string {backup_status[2]}')
        sys.exit(0)

  
def api_authenticate(apikey, username):

    # Creates an instance of PoolManager that handles the http/https connection pool
    http = urllib3.PoolManager()

    api_authentication_endpoint=(f'https://identity.api.rackspacecloud.com/v2.0/tokens')
    headers = {'Content-Type': 'application/json'}

    # Encoded json payload
    authentication_payload =  json.dumps({'auth': 
                            {'RAX-KSKEY:apiKeyCredentials': 
                                {'username': username, 
                                 'apiKey': apikey
                                }
                            }
                          }).encode('utf-8')

    # Making the POST request to the Cloud API
    auth_req = http.request('POST', api_authentication_endpoint, body=authentication_payload, headers=headers)

    if auth_req.status == 200:
        # API json response
        api_resp = json.loads(auth_req.data.decode('utf-8'))

        # Extract the api_auth token
        auth_token = api_resp['access']['token']['id']

        # Extract tenant_id "account#"
        tenant_id = api_resp['access']['token']['tenant']['id']
    else:
        print(f'API Request Failed! HTTP Status: {auth_req.status}')
        sys.exit(1)

    return auth_token, tenant_id


# method that performs the API request
def api_request(endpoint, auth_token):

    # Creates an instance of PoolManager that handles the http/https connection pool
    http = urllib3.PoolManager()

    headers = {'Content-Type': 'application/json',
               'X-Auth-Token': auth_token}

    # API request
    request = http.request('GET', endpoint, headers=headers)

    # Decode API response
    api_resp = json.loads(request.data.decode('utf-8'))

    if request.status == 200:
        # API json response
        return api_resp
    else:
        print(f'API Request Failed! HTTP Status: {request.status}')
        print(f'API Error: {api_resp}')
        sys.exit(1) 


def validate_instance_presence(tenant_id, region, instance_id, ha_group_id, auth_token):

    if instance_id is not None:
        endpoint=(f'https://{region}.databases.api.rackspacecloud.com/v1.0/{tenant_id}/instances/{instance_id}')
    elif ha_group_id is not None:
        endpoint=(f'https://{region}.databases.api.rackspacecloud.com/v1.0/{tenant_id}/ha/{ha_group_id}')

    api_resp = api_request(endpoint, auth_token)

    # Check if api request returned any information on the requested instance.
    if 'itemNotFound' in api_resp:
        error = api_resp['itemNotFound']['message']
        print(f'{error}')
        return False
    else:
        return True


def get_backups(tenant_id, region, instance_id, ha_group_id, auth_token):
  
    if instance_id is not None:
        endpoint=(f'https://{region}.databases.api.rackspacecloud.com/v1.0/{tenant_id}/instances/{instance_id}/backups')
    elif ha_group_id is not None:
        endpoint=(f'https://{region}.databases.api.rackspacecloud.com/v1.0/{tenant_id}/ha/{ha_group_id}/backups')
    
    api_resp = api_request(endpoint, auth_token)

    # Checks if a recent backups exists
    if not api_resp.get('backups'):
        print(f'No backups were found for the specified dbaas instance.')
        sys.exit(1)
    else:
        backup_date = api_resp['backups'][0]['updated']
        backup_status = api_resp['backups'][0]['status']
        backup_name = api_resp['backups'][0]['name']

    return backup_status, backup_date, backup_name


if __name__ == '__main__':
    cli()
