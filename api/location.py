from google.appengine.ext import ndb

class Location(ndb.Model):
    """A model for representing locations"""
    country = ndb.StringProperty(indexed=True)
    countryCode = ndb.StringProperty(indexed=True)
    name = ndb.StringProperty(indexed=True)
    parentid = ndb.IntegerProperty(indexed=True)
    placeTypeCode = ndb.IntegerProperty(indexed=True)
    placeTypeName = ndb.StringProperty(indexed=True)
    url = ndb.StringProperty(indexed=False)
    woeid = ndb.IntegerProperty(indexed=True)

    def to_dict(self):
        dict = super(Location, self).to_dict()
        dict['placeType'] = {
                'code': self.placeTypeCode,
                'name': self.placeTypeName
        }
        return dict
