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
                payload='grant_type=client_credentials',
                headers={'Authorization': 'Basic: ' + bearer_token_credentials})

        if response.status_code == 200:
            # parse JSON response
            data = json.load(response.data)

            # check for access token on data
            if 'token_type' in data and data['token_type'] == 'bearer' and 'access_token' in data:
                self.bearer_token = data['access_token']
            else:
                self.bearer_token = None
