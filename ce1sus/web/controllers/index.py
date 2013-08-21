"""module holding all controllers needed for the index handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.web.controllers.base import BaseController
import cherrypy
from cherrypy._cperror import HTTPRedirect
from ce1sus.web.helpers.protection import Protector
from ce1sus.brokers.permissionbroker import UserBroker
import datetime
from ce1sus.web.helpers.protection import require

class IndexController(BaseController):
  """index controller handling all actions in the index section"""

  def __init__(self):
    BaseController.__init__(self)
    self.userBroker = self.brokerFactory(UserBroker)

  @cherrypy.expose
  def index(self, errorMsg=None):
    """
    The index page of ce1sus. Mainly only an login page

    :param errorMsg: Error message to be displayed
    :type errorMsg: String

    :returns: generated HTML
    """
    return self.login(errorMsg)

  @cherrypy.expose
  def login(self, errorMsg=None):
    template = self.getTemplate('/index/login.html')
    return template.render(errorMsg=errorMsg)


  @cherrypy.expose
  def doLogin(self, username=None, password=None):
    """
    Login of the page. This function checks if the credentials are valid and
    if so sets a session for the user. Also redirects the user to the index page
    of the internal site.

    :param username: the username
    :type username: String
    :param password: the password of the user (paintext?)
    :type password: String

    """
    if username is None or password is None:
      raise HTTPRedirect('/index')

    errorMsg = self.checkCredentials(username, password)
    if errorMsg:
      return self.index(errorMsg)
    else:
      user = self.userBroker.getUserByUserName(username)
      user.last_login = datetime.datetime.now()
      self.userBroker.update(user)
      Protector.setSession(username)
      raise HTTPRedirect('/internal')

  @cherrypy.expose
  def logout(self):
    self.clearSession()
    raise HTTPRedirect('/')

  @require()
  @cherrypy.expose
  def internal(self):
    template = self.getTemplate('/index/basePage.html')
    return template.render()



