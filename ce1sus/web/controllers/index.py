from ce1sus.web.controllers.base import BaseController
import cherrypy
from cherrypy._cperror import HTTPRedirect

class IndexController(BaseController):
  
  @cherrypy.expose
  def index(self):
    template = self.mako.getTemplate('/index/index.html')
    return template.render()
  
  @cherrypy.expose
  def doLogin(self, username=None, password=None):
    raise HTTPRedirect('/index/main')
    
  @cherrypy.expose
  def main(self):
    template = self.mako.getTemplate('/index/index.html')
    return template.render()
  
