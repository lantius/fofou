from google.appengine.ext import db

class FofouUser(db.Model):
  user = db.UserProperty()
  # name, as entered in the post form
  name = db.StringProperty()
  # value of 'remember_me' checkbox selected during most recent post
  remember_me = db.BooleanProperty(default=True)