import os
from google.appengine.api import memcache
from google.appengine.api import users

from base import FofouBase
from models.forum import Forum
from models.topic import Topic

# responds to /<forumurl>/[?from=<from>]
# shows a list of topics, potentially starting from topic N
class TopicList(FofouBase):
  def get(self):
    (forum, siteroot, tmpldir) = self.forum_siteroot_tmpldir_from_url(self.request.path_info)
    if not forum or forum.is_disabled:
      return self.redirect("/")
    off = self.request.get("from") or 0
    user = users.get_current_user()
    is_moderator = users.is_current_user_admin()
    MAX_TOPICS = 75
    (topics, new_off) = self.get_topics_for_forum(forum, is_moderator, off, MAX_TOPICS)
    forum.title_or_url = forum.title or forum.url
    tvals = {
      'siteroot' : siteroot,
      'siteurl' : self.request.url,
      'forum' : forum,
      'topics' : topics,
      'analytics_code' : forum.analytics_code or "",
      'new_from' : new_off,
      'log_in_out' : self.get_log_in_out(siteroot),
      'user': user
    }
    tmpl = os.path.join(tmpldir, "topic_list.html")
    self.template_out(tmpl, tvals)
    

  # returns (topics, new_off)
  def get_topics_for_forum(self, forum, is_moderator, off, count):
    off = int(off)
    key = forum.topics_memcache_key()
    topics = memcache.get(key)
    if not topics:
      q = Topic.gql("WHERE forum = :1 ORDER BY created_on DESC", forum)
      topics = q.fetch(1000)
      if topics:
        memcache.set(key, topics) # TODO: should I pickle?
    if not topics:
      return (None, 0)
    if topics and not is_moderator:
      topics = [t for t in topics if not t.is_deleted]
    topics = topics[off:off+count]
    new_off = off + len(topics)
    if len(topics) < count:
      new_off = None # signal this is the last page
    return (topics, new_off)
