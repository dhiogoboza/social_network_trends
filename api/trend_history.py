from google.appengine.ext import ndb

from location import Location
from trend import Trend

class TrendHistory(ndb.Model):
    """A model for representing history of trends search by place"""
    date = ndb.DateProperty(indexed=True)
    trends = ndb.StructuredProperty(Trend, repeated=True)
    location = ndb.StructuredProperty(Location, repeated=False)

    def to_dict(self):
        dict = super(TrendHistory, self).to_dict()
        dict['as_of'] = self.date.strftime('%Y-%m-%dT%H:%M:%SZ')
        return dict
