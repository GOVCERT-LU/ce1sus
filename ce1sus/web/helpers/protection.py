# -*- coding: utf-8 -*-

"""module providing authentication"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from dagr.db.session import SessionManager
from ce1sus.brokers.permission.userbroker import UserBroker
import thread

import re

SESSION_KEY_USERNAME = '_cp_username'
SESSION_KEY_USER = '_cp_user'
SESSION_KEY_GROUPS = '_cp_userGroups'
SESSION_KEY_DEFAULTGROUP = '_cp_defaultUserGroup'
REST_API_KEY = '_cp_restAPIKey'


class Protector(object):
  """The authentication handler for the site. Mainly taken out of the example
  of cherrypy."""

  def __init__(self, configFile):
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
  def setRestSession(apiKey):
    attribute = getattr(cherrypy, 'session')
    attribute.regenerate()
    attribute[REST_API_KEY] = apiKey

  @staticmethod
  def getRestAPIKey():
    attribute = getattr(cherrypy, 'session')
    key = attribute.get(REST_API_KEY, None)
    return key

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
    userBroker = SessionManager.getInstance().brokerFactory(UserBroker)
    user = userBroker.getUserByUserName(username)
    attribute[SESSION_KEY_USER] = user
    if user.defaultGroup is None:
      attribute[SESSION_KEY_GROUPS] = None
    else:
      attribute[SESSION_KEY_GROUPS] = user.defaultGroup.subgroups
    attribute[SESSION_KEY_DEFAULTGROUP] = user.defaultGroup

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
  def getUserGroups():
    attribute = getattr(cherrypy, 'session')
    groups = attribute.get(SESSION_KEY_GROUPS, None)
    return groups

  @staticmethod
  def getUserDefaultGroup():
    attribute = getattr(cherrypy, 'session')
    groups = attribute.get(SESSION_KEY_DEFAULTGROUP, None)
    return groups

  @staticmethod
  def clearSession():
    """
    Clears the session
    """
    username = Protector.getUserName()
    attribute = getattr(cherrypy, 'session')
    attribute[SESSION_KEY_USERNAME] = None
    attribute[SESSION_KEY_USER] = None
    attribute[SESSION_KEY_GROUPS] = None
    attribute[SESSION_KEY_DEFAULTGROUP] = None

    if username:
      cherrypy.request.login = None


  @staticmethod
  def clearRestSession():
    attribute = getattr(cherrypy, 'session')
    attribute[REST_API_KEY] = None

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
      referer = '/' + re.search(r'^http[s]?://[\w\d:]+/(.*)$',
                                referer).group(1)
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
