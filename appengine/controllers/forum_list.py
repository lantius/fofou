from google.appengine.api import users
from google.appengine.ext import db

from base import FofouBase
from models.forum import Forum

# responds to /, shows list of available forums or redirects to
# forum management page if user is admin
class ForumList(FofouBase):
  def get(self):
    if users.is_current_user_admin():
      return self.redirect("/manageforums")
    MAX_FORUMS = 256 # if you need more, tough
    forums = db.GqlQuery("SELECT * FROM Forum").fetch(MAX_FORUMS)
    for f in forums:
        f.title_or_url = f.title or f.url
    tvals = {
      'forums' : forums,
      'isadmin' : users.is_current_user_admin(),
      'log_in_out' : self.get_log_in_out("/")
    }
    self.template_out("forum_list.html", tvals)