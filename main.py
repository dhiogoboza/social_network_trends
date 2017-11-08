# Copyright 2015 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START app]
import logging
import os

from pathlib import Path

from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory

import json

import requests
from requests_oauthlib import OAuth1

import twitter

DATA_FOLDER = "data"

# Twitter API urls
URL_AVAILABLE_TRENDS = 'https://api.twitter.com/1.1/trends/available.json'

# Authorization from twitter API
auth = None

app = Flask(__name__, static_folder = 'client', static_url_path = '')

@app.route('/')
def index():
    print("index:", 'index.html')
    return app.send_static_file('index.html')

@app.route('/data', methods=['POST'])
def data():
    return get_chart(json.dumps(request.form))

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

def get_chart(data):
    print("data:", data)
    
    #print(data["subject"])
    
    #url =  'https://api.twitter.com/1.1/trends/available.json'
    #r = requests.get(url, auth=auth)
    
    #result_data = json.dumps(r.content)
    
    #print(result_data)
    
    a = ({"cols":[{"label":"Country","type":"string"},{"label":"Popularity","type":"number"}],
            "rows":[
                {"c":[{"v":"Germany"},{"v":200}]},{"c":[{"v":"United States"},{"v":300}]},
                {"c":[{"v":"Brazil"},{"v":400}]},{"c":[{"v":"Canada"},{"v":500}]},
                {"c":[{"v":"France"},{"v":600}]},{"c":[{"v":"RU"},{"v":700}
            ]}
        ]})
    
    return json.dumps(a)

def context_init():
    # Auth init
    global auth
    
    url = 'https://api.twitter.com/1.1/account/verify_credentials.json'
    auth = OAuth1(twitter.API_KEY, twitter.API_SECRET, twitter.ACCESS_TOKEN, twitter.ACCESS_TOKEN_SECRET)
    requests.get(url, auth=auth)
    
    # Locations init
    locations_file = Path(DATA_FOLDER + "/locations.dat")
    if not locations_file.exists():
        r = requests.get(URL_AVAILABLE_TRENDS, auth=auth)
        result = r.content.decode("utf-8")
        jsonResult = json.loads(result)
        # TODO create locations file
        print(jsonResult[0])

if __name__ == '__main__':
    # Init data
    context_init()

    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
