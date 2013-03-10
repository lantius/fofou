# This code is in Public Domain. Take all the code you want, I'll just write more.
import os, string, time, random, cgi, urllib, datetime, StringIO, pickle
import wsgiref.handlers
from google.appengine.api import users
from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from controllers.base import FofouBase
from controllers.manage import ManageForums
from controllers.forum_list import ForumList
from controllers.post import PostForm
from controllers.post_admin import PostAdmin
from controllers.rss import Rss
from controllers.rss_all import RssAll
from controllers.topic import TopicForm
from controllers.topic_list import TopicList
from models.user import FofouUser
from models.forum import Forum
from models.post import Post
from models.topic import Topic

# Structure of urls:
#
# Top-level urls
#
# / - list of all forums
#
# /manageforums[?forum=<key> - edit/create/disable forums
#
# Per-forum urls
#
# /<forum_url>/[?from=<n>]
#    index, lists of topics, optionally starting from topic <n>
#
# /<forum_url>/post[?id=<id>]
#    form for creating a new post. if "topic" is present, it's a post in
#    existing topic, otherwise a post starting a new topic
#
# /<forum_url>/topic?id=<id>&comments=<comments>
#    shows posts in a given topic, 'comments' is ignored (just a trick to re-use
#    browser's history to see if the topic has posts that user didn't see yet
#
# /<forum_url>/postdel?<post_id>
# /<forum_url>/postundel?<post_id>
#    delete/undelete post
#
# /<forum_url>/rss
#    rss feed for first post in the topic (default)
#
# /<forum_url>/rssall
#    rss feed for all posts

# HTTP codes
HTTP_NOT_ACCEPTABLE = 406
HTTP_NOT_FOUND = 404




def long2ip(val):
  slist = []
  for x in range(0,4):
    slist.append(str(int(val >> (24 - (x * 8)) & 0xFF)))
  return ".".join(slist)

def req_get_vals(req, names, strip=True):
  if strip:
    return [req.get(name).strip() for name in names]
  else:
    return [req.get(name) for name in names]

def fake_error(response):
  response.headers['Content-Type'] = 'text/plain'
  response.out.write('There was an error processing your request.')



def main():
  application = webapp.WSGIApplication(
     [  ('/', ForumList),
        ('/manageforums', ManageForums),
        ('/[^/]+/postdel', PostAdmin),
        ('/[^/]+/postundel', PostAdmin),
        ('/[^/]+/post', PostForm),
        ('/[^/]+/topic', TopicForm),
        ('/[^/]+/rss', Rss),
        ('/[^/]+/rssall', RssAll),
        ('/[^/]+/?', TopicList)],
     debug=True)
  wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
  main()
