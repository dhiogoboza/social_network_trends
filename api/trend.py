from google.appengine.ext import ndb

class Trend(ndb.Model):
    """A model for representing trends"""
    name = ndb.StringProperty(indexed=True)
    promoted_content = ndb.StringProperty(indexed=False)
    query_string = ndb.StringProperty(indexed=True) # 'query' conflicts with inherited ndb.Model.query method
    search_count = ndb.IntegerProperty(indexed=True)
    url = ndb.StringProperty(indexed=False)
    tweet_volume = ndb.IntegerProperty(indexed=True)

    def to_dict(self):
        dict = super(Trend, self).to_dict(exclude=['query_string'])
        dict['query'] = self.query_string
        return dict
