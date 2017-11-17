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
import time

from pathlib import Path

from flask import Flask
from flask import request
from flask import render_template
from flask import send_from_directory

import json

import requests
from requests_oauthlib import OAuth1

import twitter

DATA_FOLDER = "data/"
LOCATIONS_FILE = "locations.dat"

# Twitter API urls
URL_AUTH = 'https://api.twitter.com/1.1/account/verify_credentials.json'
URL_AVAILABLE_TRENDS = 'https://api.twitter.com/1.1/trends/available.json'
URL_TRENDS_IN_PLACE = 'https://api.twitter.com/1.1/trends/place.json?id='

# Authorization from twitter API
auth = None

# Twitter locations
locations = None

# Flask app
app = Flask(__name__, static_folder = 'client', static_url_path = '')

@app.route('/')
def index():
    print("index:", 'index.html')
    return app.send_static_file('index.html')

@app.route('/data', methods=['POST'])
def data():
    data = request.form.to_dict()
    json_data = None
    
    if (data["type"] == "locations"):
        json_data = json.dumps(locations)
    elif (data["type"] == "refreshlocations"):
        update_locations()
        json_data = json.dumps(locations)
    else:
        json_data = get_chart(data)

    return json_data

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

def get_trend_key(item):
    return item["tweet_volume"]

def get_trends_in_place(subject_lines, subject, now, woeid):
    '''
    Get trends in place based on subject, current date and place (woeid)
    https://developer.twitter.com/en/docs/trends/trends-for-location/api-reference/get-trends-place
    '''
    cache = True
    data_path = DATA_FOLDER + "reach/" + now
    if (not Path(data_path).exists()):
        os.mkdir(data_path)
        cache = False
    
    data_path = data_path + "/" + subject + "/"
    
    if (not Path(data_path).exists()):
        os.mkdir(data_path)
        cache = False
    
    data_path = data_path + str(woeid) + ".dat"
    
    if (cache and Path(data_path).exists()):
        with open(data_path) as json_file:  
            return json.load(json_file)
    
    # If data is not in cache do request
    r = requests.get(URL_TRENDS_IN_PLACE + str(woeid), auth=auth)
    result = json.loads(r.content.decode("utf-8"))
    
    if (isinstance(result, list)):
        # Cache result
        print(data_path)
        with open(data_path, 'w') as outfile:  
            json.dump(result, outfile)
        
        # Register at subject map
        i = 0
        found = False
        for line in subject_lines:
            split = line.split("=")
            if (split[0] == str(woeid)):
                split = split[1].split(',')
                if not now in split:
                    subject_lines[i] = line + "," + now
                    found = True
            i = i + 1
        
        if not found:
            subject_lines.append(str(woeid) + "=" + now)
        
        return result
    else:
        print("Error:", result)
    
    return ""

def get_chart(data):
    print("data:", data)
    
    if (data["type"] == "reach"):
        reach_data_folder = DATA_FOLDER + "reach/"
        
        if (not Path(reach_data_folder).exists()):
            os.mkdir(reach_data_folder)
        
        subject_map = reach_data_folder + data["subject"] + ".map"
        subject_lines = []
        data_map_file = Path(subject_map)
        now = str(time.strftime("%d-%m-%Y"))
        
        if (data_map_file.exists()):
            with open(subject_map) as f:
                for line in f:
                    subject_lines.append(line)
        else:
            open(subject_map, 'a').close()

        all_data = []
        for location in locations:
            print("location:", location["woeid"], "-", location["parentid"])
            
            if (location["parentid"] != 1):
                result = get_trends_in_place(subject_lines, data["subject"], now, location["woeid"])
                
                if (result != ""):
                    all_location_data = []                    
                    for trend in result[0]["trends"]:
                        current_data = {}
                        current_data["name"] = trend["name"]
                        current_data["tweet_volume"] = trend["tweet_volume"] if trend["tweet_volume"]!=None else 0
                        all_location_data.append(current_data)
                    
                    all_location_data = sorted(all_location_data, key=get_trend_key, reverse=True)
                    #print("all_location_data",all_location_data)
                    
                    rate = 100
                    for trend in all_location_data:
                        if (trend["name"] == data["subject"]):
                            break
                        rate = rate - 2
                    
                    location_data = {"country": location["country"], "rate": rate}
                    
                    all_data.append(location_data)
                else:
                    break;
        
            
        print("all_data:", all_data)
        
        # Save subject map
        data_map_file = open(subject_map, 'w')
        for line in subject_lines:
            data_map_file.write("%s\n" % line)
        
        chart_data = ({"cols":[{"label":"Country","type":"string"},{"label":"Popularity","type":"number"}],
            "rows":[
                {"c":[{"v":"Germany"},{"v":200}]},{"c":[{"v":"United States"},{"v":300}]},
                {"c":[{"v":"Brazil"},{"v":400}]},{"c":[{"v":"Canada"},{"v":500}]},
                {"c":[{"v":"France"},{"v":600}]},{"c":[{"v":"RU"},{"v":700}
            ]}
        ]})
            
        return json.dumps(chart_data)
        
    return ""

def load_locations():
    global locations
    
    with open(DATA_FOLDER + LOCATIONS_FILE) as json_file:  
        locations = json.load(json_file)
    
def update_locations():
    global locations
    
    r = requests.get(URL_AVAILABLE_TRENDS, auth=auth)
    result = r.content.decode("utf-8")
    locations = json.loads(result)
    
    with open(DATA_FOLDER + LOCATIONS_FILE, 'w') as outfile:  
        json.dump(locations, outfile)

def context_init():
    # Auth init
    global auth
    
    url = URL_AUTH
    auth = OAuth1(twitter.API_KEY, twitter.API_SECRET, twitter.ACCESS_TOKEN, twitter.ACCESS_TOKEN_SECRET)
    requests.get(url, auth=auth)
    
    # Create /data folder if not exists
    if not Path(DATA_FOLDER).exists():
        os.mkdir(DATA_FOLDER)

    # Locations init
    locations_file = Path(DATA_FOLDER + LOCATIONS_FILE)
    if not locations_file.exists():
        update_locations()
    else:
        load_locations()

if __name__ == '__main__':
    # Init data
    context_init()

    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
