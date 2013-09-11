# -*- coding: utf-8 -*-

"""
module handing the index pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.web.controllers.base import BaseController
import cherrypy
from cherrypy._cperror import HTTPRedirect
from ce1sus.web.helpers.protection import Protector
from ce1sus.brokers.permissionbroker import UserBroker
import datetime
from ce1sus.web.helpers.protection import require
from dagr.db.broker import NothingFoundException, BrokerException
from dagr.helpers.ldaphandling import LDAPHandler
from dagr.db.session import SessionManager

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
    """
    Renders the login Page

    :returns: generated HTML
    """
    template = self.getTemplate('/index/login.html')
    Protector.clearSession()
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

  def checkCredentials(self, username=None, password=None):
    """
    Checks if the credentials are vaild

    :param username: The username
    :type username: String
    :param password: The password of the user in plain text?
    :typee password: String

    :returns: Boolean
    """



    # Verifies credentials for username and password.
    # Returns None on success or a string describing the error on failure
    # Adapt to your needs
    try:
      userBroker = SessionManager.brokerFactory(UserBroker)
      user = userBroker.getUserByUsernameAndPassword(username, 'EXTERNALAUTH')
      if user is None:
        raise NothingFoundException
      # ok it is an LDAPUser
      lh = LDAPHandler.getInstance()
      lh.open()
      valid = lh.isUserValid(username, password)
      lh.close()

      # an exception is raised as the remaining procedure is similar
      if not valid:
        raise NothingFoundException("Username or password are not valid")

    except NothingFoundException:
      # ok it's not an LDAP User
      try:
        userBroker = SessionManager.brokerFactory(UserBroker)
        user = userBroker.getUserByUsernameAndPassword(username, password)
        if user is None:
          raise BrokerException
      except BrokerException:
        return "Incorrect username or password."
      if user.disabled == 1:
        return "Incorrect username or password."
    return None

  @require()
  @cherrypy.expose
  def logout(self):
    """
    Log out method
    """
    self.clearSession()
    raise HTTPRedirect('/')

  @require()
  @cherrypy.expose
  def internal(self):
    """
    Renders the base for the whole page in the internal section

    :returns: generated HTML
    """
    template = self.getTemplate('/index/basePage.html')
    return template.render()
