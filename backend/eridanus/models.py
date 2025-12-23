from google.cloud import ndb


class BaseModel(ndb.Model):
    usernickname = ndb.StringProperty()
    creation_datetime = ndb.DateTimeProperty()


class Weight(BaseModel):
    # https://cloud.google.com/appengine/docs/standard/python/ndb/entity-property-reference
    weight = ndb.FloatProperty()
    weighing_date = ndb.DateProperty()


class Activity(BaseModel):
    activity_date = ndb.DateProperty()
    activity_time = ndb.TimeProperty()
    duration = ndb.IntegerProperty()
    calories = ndb.IntegerProperty()
    notes = ndb.StringProperty()


class Run(Activity):
    distance = ndb.FloatProperty()
    # speed = ndb.ComputedProperty(lambda self: self.distance/(self.time/60))
    speed = ndb.FloatProperty()
    notes = ndb.StringProperty()


class PushUp(Activity):
    count = ndb.IntegerProperty()


class Crunch(Activity):
    count = ndb.IntegerProperty()


class JumpingRope(Activity):
    count = ndb.IntegerProperty()
