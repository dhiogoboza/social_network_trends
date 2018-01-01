from google.appengine.ext import ndb

from location import Location
from trend import Trend

class TrendHistory(ndb.Model):
    """A model for representing history of trends search by place"""
    date = ndb.DateProperty(indexed=True)
    trends = ndb.StructuredProperty(Trend, repeated=True)
    location = ndb.StructuredProperty(Location, repeated=False, indexed=True)

    def to_dict(self):
        dict = super(TrendHistory, self).to_dict(exclude=['date'])
        dict['as_of'] = self.date.strftime('%Y-%m-%dT%H:%M:%SZ')
        dict['locations'] = [dict['location']]
        del dict['location']
        return dict
