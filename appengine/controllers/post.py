import os, sha
from google.appengine.ext import db
from google.appengine.api import memcache
from google.appengine.api import users

from base import FofouBase
from models.post import Post
from models.topic import Topic
from models.user import FofouUser

# responds to /<forumurl>/post[?id=<topic_id>]
class PostForm(FofouBase):

  def get(self):
    (forum, siteroot, tmpldir) = self.forum_siteroot_tmpldir_from_url(self.request.path_info)
    if not forum or forum.is_disabled:
      return self.redirect("/")

    rememberChecked = ""
    prevName = ""
    user = self.get_fofou_user()
    if user and user.remember_me:
      rememberChecked = "checked"
      prevName = user.name
    forum.title_or_url = forum.title or forum.url
    tvals = {
      'siteroot' : siteroot,
      'forum' : forum,
      'rememberChecked' : rememberChecked,
      'prevName' : prevName,
      'log_in_out' : self.get_log_in_out(self.request.url)
    }
    topic_id = self.request.get('id')
    if topic_id:
      topic = db.get(db.Key.from_path('Topic', int(topic_id)))
      if not topic: return self.redirect(siteroot)
      tvals['prevTopicId'] = topic_id
      tvals['prevSubject'] = topic.subject
    tmpl = os.path.join(tmpldir, "post.html")
    self.template_out(tmpl, tvals)

  def post(self):
    (forum, siteroot, tmpldir) = self.forum_siteroot_tmpldir_from_url(self.request.path_info)
    if not forum or forum.is_disabled:
      return self.redirect("/")
    if self.request.get('Cancel'):
      return self.redirect(siteroot)

    user_id = users.get_current_user()
    if not user_id:
      return self.redirect("/")

    vals = ['TopicId', 'Subject', 'Message', 'Remember', 'Name']
    (topic_id, subject, message, remember_me, name) = self.req_get_vals(self.request, vals)
    message = self.to_unicode(message)

    remember_me = True
    if remember_me == "": remember_me = False
    rememberChecked = ""
    if remember_me: rememberChecked = "checked"

    tvals = {
      'siteroot' : siteroot,
      'forum' : forum,
      "prevSubject" : subject,
      "prevMessage" : message,
      "rememberChecked" : rememberChecked,
      "prevName" : name,
      "prevTopicId" : topic_id,
      "log_in_out" : self.get_log_in_out(siteroot + "post")
    }

    # validate
    errclass = None
    if not message: errclass = "message_class"
    if not name: errclass = "name_class"
    # first post must have subject
    if not topic_id and not subject: errclass = "subject_class"

    # sha.new() doesn't accept Unicode strings, so convert to utf8 first
    message_utf8 = message.encode('UTF-8')
    s = sha.new(message_utf8)
    sha1_digest = s.hexdigest()

    duppost = Post.gql("WHERE sha1_digest = :1", sha1_digest).get()
    if duppost: errclass = "message_class"

    if errclass:
      tvals[errclass] = "error"
      tmpl = os.path.join(tmpldir, "post.html")
      return self.template_out(tmpl, tvals)

    existing_user = False
    user_id = users.get_current_user()
    if user_id:
      user = FofouUser.gql("WHERE user = :1", user_id).get()
      if not user:
        #logging.info("Creating new user for '%s'" % str(user_id))
        user = FofouUser(user=user_id, remember_me = remember_me, name=name)
        user.put()
      else:
        existing_user = True
        #logging.info("Found existing user for '%s'" % str(user_id))

    if existing_user:
      need_update = False
      if user.remember_me != remember_me:
        user.remember_me = remember_me
        need_update = True
      if user.name != name:
        user.name = name
        need_update = True
      if need_update:
        #logging.info("User needed an update")
        user.put()

    if not topic_id:
      topic = Topic(forum=forum, subject=subject, created_by=name)
      topic.put()
    else:
      topic = db.get(db.Key.from_path('Topic', int(topic_id)))
      #assert forum.key() == topic.forum.key()
      topic.ncomments += 1
      topic.put()

    user_ip_str = self.get_remote_ip()
    p = Post(topic=topic, forum=forum, user=user, user_ip=0, user_ip_str=user_ip_str, message=message, sha1_digest=sha1_digest, user_name = name)
    p.put()

    forum.clear_rss_memcache()
    forum.clear_topics_memcache()
    if topic_id:
      self.redirect(siteroot + "topic?id=" + str(topic_id))
    else:
      self.redirect(siteroot)
      
  def get_remote_ip(self): return os.environ['REMOTE_ADDR']
  