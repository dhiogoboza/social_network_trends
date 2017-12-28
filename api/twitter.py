from urllib import quote
from base64 import b64encode
import json

class TwitterAPI:
    """
    Twitter API class
    """

    """
    Safe string to use on urllib.quote
    """
    SAFE_QUOTE_STRING = '~@#$&()*!+=:;,.?/\''

    class Requestor:
        """
        Twitter API Request class
        """

        GET = 1
        POST = 2
        HEAD = 3
        PUT = 4
        DELETE = 5
        PATCH = 6

        def request(self, url, payload=None, method=1,
                headers={}, follow_redirects=True, validate_certificate=None):
            """
            Requests the given HTTP URL, blocking until the result is returned.

            Return:
            An TwitterAPI.Response instance
            """
            pass

    class Response:
        """
        Twitter API Response class
        """

        def __init__(self, data, status_code, headers={}):
            """
            Twitter API Response constructor
            """
            self.data = data
            self.status_code = status_code
            self.headers = headers

    class UnauthenticatedError(Exception):
        """
        UnauthenticatedError for Twitter API

        Thrown when a method that requires authentication is called
        without bearer_token
        """

        def __init__(self):
            self.value = 'Session is not authenticated. Call auth() with proper configuration'

        def __str__(self):
            return repr(self.value)

    def __init__(self, options, requestor):
        """
        Twitter API constructor
        """
        self.bearer_token = None
        self.config = options
        self.requestor = requestor

    def isAuthenticated(self):
        """
        Check if this instance is properly authenticated
        on Twitter REST API - that is it has a valid bearer token
        """
        return self.bearer_token is not None

    def auth(self):
        """
        Authenticate this instance on Twitter REST API
        https://developer.twitter.com/en/docs/basics/authentication/overview/application-only
        """
        # do nothing if bearer_token exists
        if self.isAuthenticated():
            return

        # encode consumer key
        urlencoded_consumer_key = quote(self.config['consumer_key'],
                safe=TwitterAPI.SAFE_QUOTE_STRING)

        # encode consumer secret
        urlencoded_consumer_secret = quote(self.config['consumer_secret'],
                safe=TwitterAPI.SAFE_QUOTE_STRING)

        # generate bearer token credentials
        bearer_token_credentials = urlencoded_consumer_key + ":" + urlencoded_consumer_secret
        bearer_token_credentials = b64encode(bearer_token_credentials)

        # request bearer token
        # TODO(ruben): handle exceptions, ie timeout and etc
        response = self.requestor.request('https://api.twitter.com/oauth2/token',
                method=TwitterAPI.Requestor.POST,
                payload='grant_type=client_credentials',
                headers={'Authorization': 'Basic ' + bearer_token_credentials,
                        'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8'})

        if response.status_code == 200:
            # parse JSON response
            data = json.loads(response.data)

            # check for access token on data
            if 'token_type' in data and data['token_type'] == 'bearer' and 'access_token' in data:
                self.bearer_token = data['access_token']
            else:
                self.bearer_token = None

    def get_trends_place(self, woeid):
        """
        Returns the top 50 trending topics for a specific WOEID, if trending
        information is available for it.

        https://developer.twitter.com/en/docs/trends/trends-for-location/api-reference/get-trends-place

        WOEID stands for Yahoo! Where On Earth ID of the location to return
        trending information for.
        Global information is available by using 1 as the WOEID.
        See more on http://developer.yahoo.com/geo/geoplanet/
        """

        # raise unauthenticated error if not properly authenticated
        if not self.isAuthenticated():
            raise UnauthenticatedError()

        # request trends information for location
        # TODO(ruben): handle exceptions, ie timeout and etc
        response = self.requestor.request('https://api.twitter.com/1.1/trends/place.json?id=' + woeid,
                headers={'Authorization': 'Bearer ' + b64encode(self.bearer_token)})

        if response.status_code == 200:
            return response.data
        else:
            return '[]'

    def get_trends_available(self):
        """
        Returns the locations that Twitter has trending topic information for.

        https://developer.twitter.com/en/docs/trends/locations-with-trending-topics/api-reference/get-trends-available

        The response is an array of "locations" that encode the location's WOEID
        and some other human-readable information such as a canonical name and
        country the location belongs in.

        WOEID stands for Yahoo! Where On Earth ID of the location to return
        trending information for.
        See more on http://developer.yahoo.com/geo/geoplanet/
        """

        # raise unauthenticated error if not properly authenticated
        if not self.isAuthenticated():
            raise UnauthenticatedError()

        # request places with trends information available
        # TODO(ruben): handle exceptions, ie timeout and etc
        response = self.requestor.request('https://api.twitter.com/1.1/trends/available.json',
                headers={'Authorization': 'Bearer ' + b64encode(self.bearer_token)})

        if response.status_code == 200:
            return response.data
        else:
            return '[]'
