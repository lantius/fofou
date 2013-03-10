import os
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

from models.forum import Forum
from models.user import FofouUser


class FofouBase(webapp.RequestHandler):
  def get_fofou_user(self):
    # get user by google user id
    user_id = users.get_current_user()
    user = None
    if user_id:
      user = FofouUser.gql("WHERE user = :1", user_id).get()
      #if user: logging.info("Found existing user for by user_id '%s'" % str(user_id))
    return user

  def template_out(self, template_name, template_values):
    self.response.headers['Content-Type'] = 'text/html'
    #path = os.path.join(os.path.dirname(__file__), template_name)
    path = template_name
    #logging.info("tmpl: %s" % path)
    res = template.render(path, template_values)
    self.response.out.write(res)

  def req_get_vals(self, req, names, strip=True):
    if strip:
      return [req.get(name).strip() for name in names]
    else:
      return [req.get(name) for name in names]
  
  def get_log_in_out(self, url):
    user = users.get_current_user()
    if user:
      if users.is_current_user_admin():
        return "Welcome admin, %s! <a href=\"%s\">Log out</a>" % (user.nickname(), users.create_logout_url(url))
      else:
        return "Welcome, %s! <a href=\"%s\">Log out</a>" % (user.nickname(), users.create_logout_url(url))
    else:
      return "<a href=\"%s\">Log in</a>" % users.create_login_url(url)

  def forum_siteroot_tmpldir_from_url(self, url):
    SKINS = ["default"]

    assert '/' == url[0]
    path = url[1:]
    if '/' in path:
      (forumurl, rest) = path.split("/", 1)
    else:
      forumurl = path
    forum = Forum.get_forum_by_url(forumurl)
    if not forum:
      return (None, None, None)
    siteroot = "/" + forum.url + "/"
    skin_name = forum.skin
    if skin_name not in SKINS:
      skin_name = SKINS[0]
    tmpldir = os.path.join("skins", skin_name)
    return (forum, siteroot, tmpldir)

  def my_hostname(self):
      # TODO: handle https as well
      h = "http://" + os.environ["SERVER_NAME"];
      port = os.environ["SERVER_PORT"]
      if port != "80":
          h += ":%s" % port
      return h
    

  def to_unicode(self, val):
    if isinstance(val, unicode): return val
    try:
      return unicode(val, 'latin-1')
    except:
      pass
    try:
      return unicode(val, 'ascii')
    except:
      pass
    try:
      return unicode(val, 'utf-8')
    except:
      raise
