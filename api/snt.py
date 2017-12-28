## Social Network Trends API
#

import webapp2
import logging
from urlparse import parse_qs

from google.appengine.api import urlfetch

from twitter import TwitterAPI
import twitter_credentials

class URLFetchRequestor(TwitterAPI.Requestor):
    def request(self, url, payload=None, method=1,
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
    # FIXME: load_locations
    print("FIXME: load_locations")
    return []

def update_locations():
    # FIXME: update_locations
    print("FIXME: update_locations")
    return []

def get_chart(data):
    # FIXME: get_chart
    print("FIXME: get_chart")
    return '[]'

class SNTDataHandler(webapp2.RequestHandler):
    def post(self):
        if not twitter_api.isAuthenticated():
            twitter_api.auth()

        data = parse_qs(self.request.body)
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
