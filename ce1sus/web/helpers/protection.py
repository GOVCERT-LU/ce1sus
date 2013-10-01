"""module providing authentication"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from dagr.db.session import SessionManager
from ce1sus.brokers.permissionbroker import UserBroker
import re

SESSION_KEY_USERNAME = '_cp_username'
SESSION_KEY_USER = '_cp_user'
SESSION_KEY_GROUPS = '_cp_userGroups'

class Protector(object):
  """The authentication handler for the site. Mainly taken out of the example
  of cherrypy."""

  def __init__(self, configFile):
    # TODO: Fixme completely
    cherrypy.tools.auth = cherrypy.Tool('before_handler', Protector.check_auth)

  # pylint: disable=W0613
  @staticmethod
  def check_auth(*args, **kwargs):
    """A tool that looks in config for 'auth.require'. If found and it
    is not None, a login is required and the entry is evaluated as a list of
    conditions that the user must fulfill"""
    conditions = cherrypy.request.config.get('auth.require', None)
    if conditions is not None:
      attribute = getattr(cherrypy, 'session')
      username = attribute.get(SESSION_KEY_USERNAME)
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
    attribute[SESSION_KEY_USERNAME] = cherrypy.request.login = username
    userBroker = SessionManager.brokerFactory(UserBroker)
    user = userBroker.getUserByUserName(username)
    attribute[SESSION_KEY_USER] = user
    attribute[SESSION_KEY_GROUPS] = user.groups


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
    attribute = getattr(cherrypy, 'session')
    user = attribute.get(SESSION_KEY_USER, None)
    return user

  @staticmethod
  def getMaxUserTLP(groups):
    tlpLevel = 3
    if groups is None:
      return tlpLevel
    else:
      for group in groups:
        tlpLevel = min(tlpLevel, group.tlpLvl)
      return tlpLevel

  @staticmethod
  def checkIfViewable(groups, isOwner, tlp):
    """
    Checks if the group can 'view' the page, else an exception is raised.

    :param groups: The list of groups the page should be asscessible to
    :type gourps: list
    """

    if isOwner:
      result = True
    else:
      attribute = getattr(cherrypy, 'session')
      groups = attribute.get(SESSION_KEY_GROUPS, None)
      result = Protector.getMaxUserTLP(groups) == tlp.identifier
      if not result:
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
    if not result:
      raise cherrypy.HTTPError(403)

  @staticmethod
  def clearSession():
    """
    Clears the session
    """
    username = Protector.getUserName()
    attribute = getattr(cherrypy, 'session')
    attribute[SESSION_KEY_USERNAME] = None
    if username:
      cherrypy.request.login = None

# pylint: disable=W0212
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
    user = Protector.getUser()
    return user.privileged
  return check

def requireReferer(allowedReferers):
  """
  Condition that verifies if the user has the privileged right set

  Note: Should only be used as condition for the require decorator
  """
  def check():
    """
      Checks if the user has the privileged right
    """
    # TODO fix this for the server
    return True
    referer = cherrypy.request.headers.elements('Referer')
    try:
      referer = referer[0].value
      referer = '/' + re.search(r'^http[s]?://[\w\d:]+/(.*)$', referer).group(1)
      if referer in allowedReferers:
        return True
      else:
        return False
    except IndexError:
      return False
  return check

# pylint: disable=W0613
def isAuthenticated(context):
  """
      Note: MAKO ONLY
  """
  username = Protector.getUserName()
  return not username is None

