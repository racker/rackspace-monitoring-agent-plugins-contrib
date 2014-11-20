#!/usr/bin/env python2.7
"""
Copyright 2014 Justin Gallardo
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

This plugin will hit the monitoring API and check for the latest state of an
alarm. If the state is OK, it will emit a metric alarm_state_ok with the
value 1. If it is not OK, it will emit a metric alarm_state_ok with the value 0.
"""
import argparse
import urllib2
import json
import sys


def main():
    las_uri = ('https://monitoring.api.rackspacecloud.com/v1.0/views/'
           'latest_alarm_states?entityId={0}').format(args.entity_id)
    auth_payload = {
        'auth':{
            'RAX-KSKEY:apiKeyCredentials':{
                'username': args.user,
                'apiKey': args.api_key
            }
        }
    }

    try:
        auth_req = urllib2.Request(args.auth_uri)
        auth_req.add_header('Content-type', 'application/json')
        auth_resp = json.loads(urllib2.urlopen(auth_req, json.dumps(auth_payload)).read())
    except urllib2.HTTPError:
        print 'status err Unable to authenticate user {0}'.format(args.user)
        sys.exit(1)
    else:
        auth_token = auth_resp['access']['token']['id']
        tenant_id = auth_resp['access']['token']['tenant']['id']

    try:
        view_req = urllib2.Request(las_uri)
        view_req.add_header('X-Auth-Token', auth_token)
        view_req.add_header('X-Tenant-Id', tenant_id)
        view_resp = json.loads(urllib2.urlopen(view_req).read())
    except urllib2.HTTPError:
        print 'status err Unable to get latest alarm states for entity {0}'.format(args.entity_id)
        sys.exit(1)
    else:
        alarm_state = None

        for las in view_resp['values'][0]['latest_alarm_states']:
            if las['alarm_id'] == args.alarm_id:
                alarm_state = las['state']
                break

        if not alarm_state:
            print 'status err No latest alarm state for alarm {0}'.format(args.alarm_id)
            sys.exit(1)

        print 'status Successfully grabbed latest alarm state for {0}:{1}'.format(args.entity_id, args.alarm_id)
        if alarm_state == 'OK':
            print 'metric alarm_state_ok int 1'
        else:
            print 'metric alarm_state_ok int 0'


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Latest alarm state plugin')
    parser.add_argument('--entity-id', dest='entity_id', action='store',
                        required=True, help='The entity id')
    parser.add_argument('--alarm-id', dest='alarm_id', action='store',
                        required=True, help='The alarm id')
    parser.add_argument('--user', dest='user', action='store',
                        required=True, help='The Rackspace user')
    parser.add_argument('--api-key', dest='api_key', action='store',
                        required=True, help='The Rackspace API key')
    parser.add_argument('--auth-uri', dest='auth_uri', action='store',
                    default='https://identity.api.rackspacecloud.com/v2.0/tokens',
                    help='The Rackspace Identity token endpoint')

    args = parser.parse_args()

    main()
