from google.appengine.api import memcache
from google.appengine.ext import db

class Forum(db.Model):
  __FORUMS_MEMCACHE_KEY = "fo"

  @staticmethod
  def clear_forums_memcache():
    memcache.delete(Forum.__FORUMS_MEMCACHE_KEY)
  
  @staticmethod
  def get_forum_by_url(forumurl):
    # number of forums is small, so we cache all of them
    forums = memcache.get(Forum.__FORUMS_MEMCACHE_KEY)
    if not forums:
      forums = Forum.all().fetch(200) # this effectively limits number of forums to 200
      if not forums:
        return None

      memcache.set(Forum.__FORUMS_MEMCACHE_KEY, forums)
    for forum in forums:
      if forumurl == forum.url:
        return forum
    return None

  def topics_memcache_key(self):
    return "to" + str(self.key().id())

  def rss_memcache_key(self):
    return "rss" + str(self.key().id())

  def clear_topics_memcache(self):
    memcache.delete(self.topics_memcache_key())

  def clear_rss_memcache(self):
    memcache.delete(self.rss_memcache_key())

  # Urls for forums are in the form /<urlpart>/<rest>
  url = db.StringProperty(required=True)
  # What we show as html <title> and as main header on the page
  title = db.StringProperty()
  # a tagline is below title
  tagline = db.StringProperty()
  # stuff to display in left sidebar
  sidebar = db.TextProperty()
  # if true, forum has been disabled. We don't support deletion so that
  # forum can always be re-enabled in the future
  is_disabled = db.BooleanProperty(default=False)
  # just in case, when the forum was created. Not used.
  created_on = db.DateTimeProperty(auto_now_add=True)
  # name of the skin (must be one of SKINS)
  skin = db.StringProperty()
  # Google analytics code
  analytics_code = db.StringProperty()
