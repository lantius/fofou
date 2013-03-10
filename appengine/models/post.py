from google.appengine.ext import db
from forum import Forum
from topic import Topic
from user import FofouUser

# A topic is a collection of posts
class Post(db.Model):
  topic = db.Reference(Topic, required=True)
  forum = db.Reference(Forum, required=True)
  created_on = db.DateTimeProperty(auto_now_add=True)
  message = db.TextProperty(required=True)
  sha1_digest = db.StringProperty(required=True)
  # admin can delete/undelete posts. If first post in a topic is deleted,
  # that means the topic is deleted as well
  is_deleted = db.BooleanProperty(default=False)
  # ip address from which this post has been made
  user_ip_str = db.StringProperty(required=False)
  # user_ip is an obsolete value, only used for compat with entries created before
  # we introduced user_ip_str. If it's 0, we assume we'll use user_ip_str, otherwise
  # we'll user user_ip
  user_ip = db.IntegerProperty(required=True)

  user = db.Reference(FofouUser, required=True)
  # user_name might be different than
  # name fields in user object, since they can be changed in
  # FofouUser
  user_name = db.StringProperty()