from google.appengine.api import memcache
from django.utils import feedgenerator
from django.template import Context, Template

from base import FofouBase
from models.post import Post
from models.topic import Topic

# responds to /<forumurl>/rss, returns an RSS feed of recent topics
# (taking into account only the first post in a topic - that's what
# joelonsoftware forum rss feed does)
class Rss(FofouBase):

  def get(self):
    (forum, siteroot, tmpldir) = self.forum_siteroot_tmpldir_from_url(self.request.path_info)
    if not forum or forum.is_disabled:
      return self.error(HTTP_NOT_FOUND)

    cached_feed = memcache.get(forum.rss_memcache_key())
    if cached_feed is not None:
      self.response.headers['Content-Type'] = 'text/xml'
      self.response.out.write(cached_feed)
      return

    feed = feedgenerator.Atom1Feed(
      title = forum.title or forum.url,
      link = self.my_hostname() + siteroot + "rss",
      description = forum.tagline)

    topics = Topic.gql("WHERE forum = :1 AND is_deleted = False ORDER BY created_on DESC", forum).fetch(25)
    for topic in topics:
      title = topic.subject
      link = self.my_hostname() + siteroot + "topic?id=" + str(topic.key().id())
      first_post = Post.gql("WHERE topic = :1 ORDER BY created_on", topic).get()
      msg = first_post.message
      # TODO: a hack: using a full template to format message body.
      # There must be a way to do it using straight django APIs
      name = topic.created_by
      if name:
        t = Template("<strong>{{ name }}</strong>: {{ msg|striptags|escape|urlize|linebreaksbr }}")
      else:
        t = Template("{{ msg|striptags|escape|urlize|linebreaksbr }}")
      c = Context({"msg": msg, "name" : name})
      description = t.render(c)
      pubdate = topic.created_on
      feed.add_item(title=title, link=link, description=description, pubdate=pubdate)
    feedtxt = feed.writeString('utf-8')
    self.response.headers['Content-Type'] = 'text/xml'
    self.response.out.write(feedtxt)
    memcache.add(forum.rss_memcache_key(), feedtxt)
