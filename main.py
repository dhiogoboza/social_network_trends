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
import simpleregex
import utils

from datetime import datetime
from datetime import timedelta

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

TRENDS_PLACE_FOLDER = DATA_FOLDER + "trends_place/"
LOCATIONS_FILE = DATA_FOLDER + "locations.dat"
EVENTS_FILE = DATA_FOLDER + "events.dat"

# Twitter API urls
URL_AUTH = 'https://api.twitter.com/1.1/account/verify_credentials.json'
URL_AVAILABLE_TRENDS = 'https://api.twitter.com/1.1/trends/available.json'
URL_TRENDS_IN_PLACE = 'https://api.twitter.com/1.1/trends/place.json?id='

# Authorization from twitter API
auth = None

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
        json_data = json.dumps(load_locations())
    elif (data["type"] == "refreshlocations"):
        json_data = json.dumps(update_locations())
    else:
        json_data = get_chart(data)

    return json_data

@app.route('/tasks/update_data', methods=['GET'])
def update_data():
    data = {}
    data["type"] = "subjectinplaces"
    data["subject"] = "none"
    
    get_chart(data)
    
    return "succes"

@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500

def load_events():
    if (Path(EVENTS_FILE).exists()):
        with open(EVENTS_FILE) as json_file:  
            return json.load(json_file)
            
    events = {}
    events["items"] = []
    
    return events

def load_locations():    
    with open(LOCATIONS_FILE) as json_file:  
        return json.load(json_file)

def update_locations():
    r = requests.get(URL_AVAILABLE_TRENDS, auth=auth)
    result = r.content.decode("utf-8")
    locations = json.loads(result)
    
    with open(LOCATIONS_FILE, 'w') as outfile:  
        json.dump(locations, outfile)
        
    return locations

def get_trend_key(item):
    return item["tweet_volume"]

def get_trends_in_place(now, woeid, history=False):
    '''
    Get trends in place, current date and place (woeid)
    https://developer.twitter.com/en/docs/trends/trends-for-location/api-reference/get-trends-place
    '''
    cache = True
    data_path = TRENDS_PLACE_FOLDER + now + "/"
    if (not Path(data_path).exists() and not history):
        os.mkdir(data_path)
        cache = False
    
    data_path = data_path + str(woeid) + ".dat"
    
    if (cache and Path(data_path).exists()):
        with open(data_path) as json_file:  
            return json.load(json_file)
    
    # Only search at history
    if (history):
        return ""
    
    # If data is not in cache do request
    r = requests.get(URL_TRENDS_IN_PLACE + str(woeid), auth=auth)
    result = json.loads(r.content.decode("utf-8"))
    
    if (isinstance(result, list)):
        # Save result
        with open(data_path, 'w') as outfile:  
            json.dump(result, outfile)
        
        return result
    else:
        print("Error:", result)
    
    return ""

def get_subject_relevance_in_places(date, subject_regex, locations):
    '''
    Get subject relevance in all {locations} array
    
    @type date: string
    @param date: Date from get subject relevance
    
    @type subject_regex: json
    @param subject_regex: Simple regex with searched subject (use simpleregex.create)
    
    @type locations: array
    @param locations: Array with locations to get subject relevance
    
    @rtype: json
    @return: Json array with Google Map table to draw the map
    '''
    all_data = {}
    
    now = str(time.strftime("%d-%m-%Y"))
    history = False
    
    if (now != date):
        history = True
        
    for location in locations:
        if (location["parentid"] == 1):
            print("location:", location["woeid"])
            result = get_trends_in_place(date, location["woeid"], history=history)
            
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
                found = False
                for trend in all_location_data:
                    # Check if subjetc matches query
                    if (simpleregex.match(subject_regex, trend["name"])):
                        found = True
                        break
                    rate = rate - 2
                
                if not found:
                    rate = 0
                
                location_data = {"country": location["name"], "rate": rate}
                if (location["woeid"] in all_data):
                    location_data["rate"] = location_data["rate"] + all_data[location["woeid"]]["rate"]
                else:  
                    all_data[location["woeid"]] = location_data
            else:
                break;
    
    print("All data", date, ":", all_data)
    
    chart_data = ({
        "cols":[{"label":"Country","type":"string"},{"label":"Relevância","type":"number"}],
        "rows":[]
    })
    
    for key, location_data in all_data.items():
        location_json = {"c":[{"v": location_data["country"]},{"v": str(location_data["rate"])}]}
        chart_data["rows"].append(location_json)
        
    return chart_data

def get_chart(data):
    print("data:", data)
    
    if (data["type"] == "subjectinplaces"):
        
        subject = data["subject"].strip()
        if (subject == ""):
            return "{'error':'Empty subject'}"
        
        subject_regex = simpleregex.create(subject)
        now = str(time.strftime("%d-%m-%Y"))
        locations = load_locations()
        
        return json.dumps(get_subject_relevance_in_places(now, subject_regex, locations))
    # End subjectinplaces
    
    elif (data["type"] == "subjectinplaceshistory"):
        subject = data["subject"].strip()
        if (subject == ""):
            return "{'error':'Empty subject'}"
        
        start_date = datetime.strptime(data["starts"], "%Y-%m-%d").date()
        end_date = datetime.strptime(data["ends"], "%Y-%m-%d").date()
        
        sr = simpleregex.create(subject)
        locations = load_locations()
        
        all_data = {}
        
        for current in utils.daterange(start_date, end_date + timedelta(days=1)):
            current_str = str(current.strftime("%d-%m-%Y"))
            all_data[current_str] = get_subject_relevance_in_places(current_str, sr, locations)
        
        return json.dumps(all_data)
        
    # End subjectinplaceshistory
        
    return ""

def context_init():
    # Auth init
    global auth
    
    url = URL_AUTH
    auth = OAuth1(twitter.API_KEY, twitter.API_SECRET, twitter.ACCESS_TOKEN, twitter.ACCESS_TOKEN_SECRET)
    requests.get(url, auth=auth)
    
    # Create /data folder if not exists
    if not Path(DATA_FOLDER).exists():
        os.mkdir(DATA_FOLDER)

    # Folder to put trends daily
    if (not Path(TRENDS_PLACE_FOLDER).exists()):
        os.mkdir(TRENDS_PLACE_FOLDER)

    # Locations init
    locations_file = Path(LOCATIONS_FILE)
    if not locations_file.exists():
        update_locations()

if __name__ == '__main__':
    # Init data
    context_init()

    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END app]
