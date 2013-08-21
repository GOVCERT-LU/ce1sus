"""module providing authentication"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from framework.db.session import SessionManager
from ce1sus.brokers.permissionbroker import UserBroker
from framework.helpers.config import Configuration
from datetime import datetime
from framework.db.broker import NothingFoundException, BrokerException
from framework.helpers.ldaphandling import LDAPHandler
import re

SESSION_KEY = '_cp_username'

class Protector(object):
  """The authentication handler for the site. Mainly taken out of the example
  of cherrypy."""

  def __init__(self, configFile):
    cherrypy.tools.auth = cherrypy.Tool('before_handler', self.check_auth)
    Protector.userBroker = SessionManager.getInstance().brokerFactory(
                                                                    UserBroker)


    self.__config = Configuration(configFile, 'Protector')
    Protector.__loginURL = self.__config.get('loginurl')
    Protector.__events = self.__config.get('firstpage')


  @staticmethod
  def checkCredentials(username, password):
    """Verifies credentials for username and password.
    Returns None on success or a string describing the error on failure"""
    # Adapt to your needs
    try:
      user = Protector.userBroker.getUserByUsernameAndPassword(username,
                                                               'EXTERNALAUTH')
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
        user = Protector.userBroker.getUserByUsernameAndPassword(username,
                                                                 password)
        if user is None:
          raise BrokerException
      except BrokerException:
        return "Incorrect username or password."

    return None

  @staticmethod
  def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
      attribute = getattr(cherrypy, 'session')
      username = attribute.get(SESSION_KEY)
      if username:
        cherrypy.request.login = username
        for condition in conditions:
          # A condition is just a callable that returns true or false
          if not condition():
            raise cherrypy.HTTPError(403)
      else:
        # redirect in case the session is gone or was not set
        raise cherrypy.HTTPRedirect("/")


  @staticmethod
  def setSession(username):
    """
    Sets the session an the username for the session

    :param username: the username of the logged in user
    :type username: String
    """
    attribute = getattr(cherrypy, 'session')
    attribute.regenerate()
    attribute[SESSION_KEY] = cherrypy.request.login = username

  @staticmethod
  def getUserName():
    """
    Returns the username of the logged in user

    :returns: String
    """
    return cherrypy.request.login

  @staticmethod
  def getUser():
    """
    Returns the logged in user

    :returns: User
    """
    user = Protector.userBroker.getUserByUserName(Protector.getUserName())
    return user


  @staticmethod
  def checkIfViewable(groups, isOwner):
    """
    Checks if the group can 'view' the page, else an exception is raised.

    :param groups: The list of groups the page should be asscessible to
    :type gourps: list
    """
    if not isOwner:
      try:
        user = Protector.getUser()
        result = False
        if user.privileged:
          result = True
        else:
          for userGrp in user.groups:
            for group in groups:
              if userGrp == group:
                result = True
                break
      except:
        raise cherrypy.HTTPError(403)
    else:
      result = True
    if not result:
      raise cherrypy.HTTPError(403)

  @staticmethod
  def clearSession():
    """
    Clears the session
    """
    username = Protector.getUserName()
    attribute = getattr(cherrypy, 'session')
    attribute[SESSION_KEY] = None
    if username:
      cherrypy.request.login = None

def require(*conditions):
  """
  Decorator that verifies if the user is logged in.
  """

  def decorate(function):
    """A decorator that appends conditions to the auth.require config
    variable."""
    if not hasattr(function, '_cp_config'):
      function._cp_config = dict()
    if 'auth.require' not in function._cp_config:
      function._cp_config['auth.require'] = []
    function._cp_config['auth.require'].extend(conditions)
    return function
  return decorate

def privileged():
  """
  Condition that verifies if the user has the privileged right set

  Note: Should only be used as condition for the require decorator
  """
  def check():
    """
      Checks if the user has the privileged right
    """
    return Protector.userBroker.isUserPrivileged(Protector.getUserName())
  return check

def requireReferer(redirect, allowedReferers):
  """
  Condition that verifies if the user has the privileged right set

  Note: Should only be used as condition for the require decorator
  """
  def check():
    """
      Checks if the user has the privileged right
    """
    referer = cherrypy.request.headers.elements('Referer')
    referer = referer[0].value
    referer = '/' + re.search(r'^http[s]?://[\w\d:]+/(.*)$', referer).group(1)
    if referer in allowedReferers:
      return True
    else:
      return False
  return check

def isAuthenticated(context):
  """
      Note: MAKO ONLY
  """
  username = Protector.getUserName()
  return not username is None

