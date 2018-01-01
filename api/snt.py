## Social Network Trends API
#

from datetime import datetime
from datetime import timedelta

import json
import logging
import simpleregex
import time
from urlparse import parse_qsl
import utils
import webapp2

from google.appengine.api import urlfetch
from google.appengine.ext import ndb

from location import Location
from trend import Trend
from trend_history import TrendHistory

from twitter import TwitterAPI
import twitter_credentials

class URLFetchRequestor(TwitterAPI.Requestor):
    def request(self, url, payload=None, method=TwitterAPI.Requestor.GET,
            headers={}, follow_redirects=True, validate_certificate=None):
        """
        Requests the given HTTP URL using Google AppEngine urlfetch
        """
        response = urlfetch.fetch(url, payload=payload, method=method,
                headers=headers, follow_redirects=follow_redirects,
                validate_certificate=validate_certificate)

        return TwitterAPI.Response(data=response.content,
                status_code=response.status_code,
                headers=response.headers)

twitter_api = TwitterAPI(options={
        'consumer_key': twitter_credentials.API_KEY,
        'consumer_secret': twitter_credentials.API_SECRET},
        requestor=URLFetchRequestor())

def load_locations():
    allQuery = Location.query()
    locations = []

    for location in allQuery.iter():
        locations.append(location.to_dict())

    return locations

def update_locations():
    # FIXME(ruben): too costy operation (a lot of db write),
    # [...] should prevent user from multiple calls to this method.
    # [...] Possible workaround is to remove 'Atualizar' button from gui
    if not twitter_api.isAuthenticated():
        twitter_api.auth()

    # parse JSON
    twitter_locations = json.loads(twitter_api.get_trends_available())

    locations = []

    for twitter_location in twitter_locations:
        queryResult = Location.query(Location.woeid == twitter_location['woeid']).fetch(1)

        location = (queryResult[0] if len(queryResult) == 1 else Location())
        # FIXME(ruben): check keys before assignment
        location.country = twitter_location['country']
        location.countryCode = twitter_location['countryCode']
        location.name = twitter_location['name']
        location.parentid = twitter_location['parentid']
        location.placeTypeCode = twitter_location['placeType']['code']
        location.placeTypeName = twitter_location['placeType']['name']
        location.url = twitter_location['url']
        location.woeid = twitter_location['woeid']

        locations.append(location)

    if len(locations) > 0:
        ndb.put_multi(locations)

    return load_locations()

def get_trends_in_place(now, woeid, history=False):
    '''
    Get trends in place, current date and place (woeid)
    https://developer.twitter.com/en/docs/trends/trends-for-location/api-reference/get-trends-place
    '''
    # FIXME(ruben): get_trends_in_place
    print('get_trends_in_place:',now,history)

    queryResult = Location.query(Location.woeid == int(woeid)).fetch(1)
    location = (queryResult[0] if len(queryResult) == 1 else None)

    # check for history
    trend_history = None
    if location is not None:
        queryResult = TrendHistory.query(ndb.AND(TrendHistory.date == now,
                TrendHistory.location == location)).fetch(1)
        trend_history = (queryResult[0] if len(queryResult) == 1 else None)

    if trend_history is not None:
        result = []
        result.append(trend_history.to_dict())
        return result

    # Only search at history
    if (history):
        return ""

    # If data is not in cache do request
    if not twitter_api.isAuthenticated():
        twitter_api.auth()

    result = json.loads(twitter_api.get_trends_place(woeid))

    if (isinstance(result, list)):
        # persist result
        trends = []
        for twitter_trend in result[0]['trends']:
            queryResult = Trend.query(Trend.name == twitter_trend['name']).fetch(1)

            trend = (queryResult[0] if len(queryResult) == 1 else Trend())
            # FIXME(ruben): check keys before assignment
            trend.name = twitter_trend['name']
            trend.promoted_content = twitter_trend['promoted_content']
            trend.query_string = twitter_trend['query']
            trend.url = twitter_trend['url']
            trend.tweet_volume = twitter_trend['tweet_volume']
            # increases search count, if trend already exists
            trend.search_count = (trend.search_count + 1 if len(queryResult) == 1 else 1)

            trends.append(trend)

        if len(trends) > 0:
            ndb.put_multi(trends)

        if location is None:
            location = Location()
            location.name = result[0]['locations'][0]['name']
            location.woeid = result[0]['locations'][0]['woeid']
            location.put()

        # create trend history
        trend_history = TrendHistory()
        trend_history.date = now
        trend_history.trends = trends
        trend_history.location = location
        trend_history.put()

        return result
    else:
        print("Error:", result)

    return ""

def get_subject_relevance_in_places(date, subject_regex, locations, relative=False, all_locations=False):
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
    # FIXME(ruben): get_subject_relevance_in_places
    print('get_subject_relevance_in_places')
    return '[]'

def get_chart(data):
    # FIXME: get_chart
    print("FIXME: get_chart")

    print("data:", data)

    if (data["type"] == "subjectinplaces"):

        if "all_locations" in data:
            all_locations = True

        subject = data["subject"].strip()
        if (subject == ""):
            return "{'error':'Empty subject'}"

        subject_regex = simpleregex.create(subject)
        now = str(time.strftime("%d-%m-%Y"))
        locations = load_locations()

        return json.dumps(get_subject_relevance_in_places(now, subject_regex, locations, data["ctype"] == "r"))
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
            all_data[current_str] = get_subject_relevance_in_places(current_str, sr, locations, data["ctype"] == "r")

        return json.dumps(all_data)

    # End subjectinplaceshistory

    elif (data["type"] == "subjectsinplace"):
        date = datetime.strptime(data["date"], "%Y-%m-%d").date()
        history = date != datetime.now().date()

        data = get_trends_in_place(date, data["location"], history=history)

        return json.dumps(data[0]["trends"]) if data != "" else '{"error": "Data not found"}'

    # End subjectsinplace

    return '[]'

class SNTDataHandler(webapp2.RequestHandler):
    def post(self):
        if not twitter_api.isAuthenticated():
            twitter_api.auth()

        data = {}
        for name, value in parse_qsl(self.request.body):
            data[name] = value

        json_data = None

        if (data["type"] == "locations"):
            if 'text' in data:
                text = data["text"]
                locations = load_locations()
                new_locations = []
                for loc in locations:
                    if (text in loc["name"]):
                        new_loc = {"name": loc["name"], "id": loc["woeid"]}
                        new_locations.append(new_loc)

                json_data = json.dumps(new_locations)
            else:
                json_data = json.dumps(load_locations())
        elif (data["type"] == "refreshlocations"):
            json_data = json.dumps(update_locations())
        else:
            json_data = get_chart(data)

        if json_data is not None:
            self.response.set_status(200)
            self.response.content_type = 'application/json'
            self.response.out.write(json_data)
        else:
            self.response.set_status(500)

class SNTUpdateDataHandler(webapp2.RequestHandler):
    def get(self):
        if not twitter_api.isAuthenticated():
            twitter_api.auth()

        data = {}

        data["type"] = "subjectinplaces"
        data["subject"] = "none"
        data["ctype"] = "a"
        data["all_locations"] = True

        get_chart(data)

        self.response.set_status(200)
        self.response.out.write("success")

app = webapp2.WSGIApplication([
    (r'/api/data', SNTDataHandler),
    (r'/api/tasks/update_data', SNTUpdateDataHandler)
], debug=True)


def handle_404(request, response, exception):
    """Default handler for 404 status code"""
    logging.exception(exception)

    response.set_status(404)


def handle_500(request, response, exception):
    """Default handler for 500 status code"""
    logging.exception(exception)

    response.set_status(500)


app.error_handlers[404] = handle_404
app.error_handlers[500] = handle_500
