import os
from google.appengine.api import users
from google.appengine.ext import db

from base import FofouBase
from models.post import Post

# responds to /<forumurl>/topic?id=<id>
class TopicForm(FofouBase):

  def get(self):
    (forum, siteroot, tmpldir) = self.forum_siteroot_tmpldir_from_url(self.request.path_info)
    if not forum or forum.is_disabled:
      return self.redirect("/")
    forum.title_or_url = forum.title or forum.url

    topic_id = self.request.get('id')
    if not topic_id:
      return self.redirect(siteroot)

    topic = db.get(db.Key.from_path('Topic', int(topic_id)))
    if not topic:
      return self.redirect(siteroot)
      
    user = users.get_current_user()
    is_moderator = users.is_current_user_admin()
    if topic.is_deleted and not is_moderator:
      return self.redirect(siteroot)

    is_archived = False
    # Note: auto-archiving disabled
    #now = datetime.datetime.now()
    #week = datetime.timedelta(days=7)
    #week = datetime.timedelta(seconds=7)
    #if now > topic.created_on + week:
    #  is_archived = True

    # 200 is more than generous
    MAX_POSTS = 200
    if is_moderator:
      posts = Post.gql("WHERE forum = :1 AND topic = :2 ORDER BY created_on", forum, topic).fetch(MAX_POSTS)
    else:
      posts = Post.gql("WHERE forum = :1 AND topic = :2 AND is_deleted = False ORDER BY created_on", forum, topic).fetch(MAX_POSTS)

    if is_moderator:
        for p in posts:
            if 0 != p.user_ip:
              p.user_ip_str = long2ip(p.user_ip)

    tvals = {
      'siteroot' : siteroot,
      'forum' : forum,
      'analytics_code' : forum.analytics_code or "",
      'topic' : topic,
      'is_moderator' : is_moderator,
      'is_archived' : is_archived,
      'posts' : posts,
      'log_in_out' : self.get_log_in_out(self.request.url),
      'user': user
    }
    tmpl = os.path.join(tmpldir, "topic.html")
    self.template_out(tmpl, tvals)
