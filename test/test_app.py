# Simple case:
## 43 phone numbers
## 5k numbers

# Format Errors:
## missing message
## missing recipients
## extra param
## not json
## Empty content
## Content-Type not application/json

# Out of bounds:
# empty recipients
# more than 5k nums
# empty message

#TODO: add support for REAL uniqueness

import unittest
import os
import sys
import requests
import json
import subprocess
import pprint
import argparse

HOST = 'http://127.0.0.1:5000'
#In order to run with CURL, we generate a script with the requests
# script can easily be run doing "bash curl.sh"
CURL_FILE = 'curl.sh'

if CURL_FILE:
    try:
        os.remove(CURL_FILE)
    except:
        pass

class TestMessagesRouteEndpoint(unittest.TestCase):
    def setUp(self):
        #I am assuming the server is already running. That way I just write the
        self.endpoint = '/messages/route'
        self.url = HOST + self.endpoint
        self.pp = pprint.PrettyPrinter(indent=4)

        if CURL_FILE:
            self.curlfile = open(CURL_FILE, "a")
        else:
            self.curlfile = None

    def tearDown(self):
        if self.curlfile:
            self.curlfile.close()

    def helper_curlway_post(self, payload, run=False, content_type="application/json"):
        json_payload = json.dumps(payload)

        # Curl is not as good as requests :)
        # If you really need curl, Here is a command to copy/paste
        cmd = ('curl -g -X POST -H "Content-Type: '+content_type+'" '
                '-d \''+ json_payload + '\' ' + self.url
            )

        #print '---'
        #print cmd
        #print '---'
        self.curlfile.write(str(cmd) + '\n\n')

        if run:
            with open(os.devnull, 'w') as f:
                subprocess.check_call(cmd, shell=True, stdout=f, stderr=subprocess.STDOUT)

    def test_post_success(self):
        # 20 Numbers
        payload = {
            'message': 'Hello World',
            'recipients': [str(2134051000 + x) for x in range(20)]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_json = {"message":"Hello World","routes":[{"ip":"10.0.3.0","recipients":["2134051010","2134051011","2134051012","2134051013","2134051014","2134051015","2134051016","2134051017","2134051018","2134051019"]},{"ip":"10.0.3.0","recipients":["2134051000","2134051001","2134051002","2134051003","2134051004","2134051005","2134051006","2134051007","2134051008","2134051009"]}]}

        #pp.pprint(expected_json)
        self.assertEqual(expected_json, r.json())

        self.helper_curlway_post(payload)
        # 43 Numbers
        payload = {
            'message': 'Hello World',
            'recipients': [str(2134051000 + x) for x in range(43)]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_json = {"message":"Hello World","routes":[{"ip":"10.0.1.0","recipients":["2134051042"]},{"ip":"10.0.1.0","recipients":["2134051041"]},{"ip":"10.0.1.0","recipients":["2134051040"]},{"ip":"10.0.2.0","recipients":["2134051035","2134051036","2134051037","2134051038","2134051039"]},{"ip":"10.0.3.0","recipients":["2134051025","2134051026","2134051027","2134051028","2134051029","2134051030","2134051031","2134051032","2134051033","2134051034"]},{"ip":"10.0.4.0","recipients":["2134051000","2134051001","2134051002","2134051003","2134051004","2134051005","2134051006","2134051007","2134051008","2134051009","2134051010","2134051011","2134051012","2134051013","2134051014","2134051015","2134051016","2134051017","2134051018","2134051019","2134051020","2134051021","2134051022","2134051023","2134051024"]}]}

        #pp.pprint(expected_json)
        self.assertEqual(expected_json, r.json())

        self.helper_curlway_post(payload)
        # 5k!
        payload = {
            'message': 'Hello World',
            'recipients': [str(2134051000 + x) for x in range(5000)]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(200, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        #Not running assertEqual since expected is going to be hella long.
        # can use the curl to proofcheck :)
        self.helper_curlway_post(payload, run=True)


    def test_post_format_errors(self):
        # Content-type is not json
        payload = {
            'message': 'Hello World',
            'recipients': [str(2134051000 + x) for x in range(2)]
            }
        headers = {'content-type': 'application/xml'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "None is not of type 'object'",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload, content_type='application_xml')

        #Content is empty
        payload = {}
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "'message' is a required property",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

        #message is wrong type
        payload = {
            'message' : 12,
            'recipients': [str(2134051000 + x) for x in range(2)]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "12 is not of type 'string'",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

        #recipients is empty
        payload = {
            'message' : "12",
            'recipients': []
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "[] is too short",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

        #not parseable json
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data="Data", headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "Invalid JSON Request.",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

        #Extra parameter
        payload = {
            'message' : "12",
            'other_message' : "12",
            'recipients': [str(2134051000 + x) for x in range(20)]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "Additional properties are not allowed (u'other_message' was unexpected)",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

    def test_post_content_errors(self):
        #recipients is too full
        payload = {
            'message' : "12",
            'recipients': [str(2134051000 + x) for x in range(5001)]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "'recipients' array is too long.",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

        #One number is wrong:
        payload = {
            'message' : "12",
            'recipients': ["222"]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "Invalid value: '222'. Must respect pattern '^(\\+1 ?)?\\(?([2-9][0-9]{2})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

        #multiple numbers are wrong (only report the first.):
        payload = {
            'message' : "12",
            'recipients': ["222", "333"]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "Invalid value: '222'. Must respect pattern '^(\\+1 ?)?\\(?([2-9][0-9]{2})\\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

        #Twice the same number:
        payload = {
            'message' : "12",
            'recipients': ["2134445654", "2134445654"]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "Values of 'recipients' must be unique",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

        #Twice the same number (in different format):
        payload = {
            'message' : "12",
            'recipients': ["(213)444-5654", "2134445654"]
            }
        headers = {'content-type': 'application/json'}

        r = requests.post(self.url, data=json.dumps(payload), headers=headers)
        self.assertEqual(400, r.status_code)
        self.assertEqual('application/json', r.headers['Content-Type'])

        expected_error = {
            'see_also': 'http://developers.domain.tld/doc/api/',
            'message': "Values of 'recipients' must be unique",
            'error': "Bad Request"}

        self.assertEqual(expected_error, r.json())
        self.helper_curlway_post(payload)

if __name__ == '__main__':
    #TODO use nosetests?
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', action='store', default=None)
    parser.add_argument('--curlfile', action='store', default=None)
    parser.add_argument('ut_args', metavar='test', nargs="*", help="unittest default args")
    args = parser.parse_args()

    ut_argv = [sys.argv[0]]

    if args.host:
        HOST = args.host

    if args.curlfile:
        CURL_FILE = args.curlfile

    ut_argv = ut_argv + args.ut_args

    unittest.main(argv=ut_argv)