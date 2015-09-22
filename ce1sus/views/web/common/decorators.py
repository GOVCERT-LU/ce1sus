# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy

SESSION_KEY = '_cp_username'
SESSION_CONFIG = '_cp_config'
SESSION_USER = '_cp_user'


def check_auth(*args, **kwargs):
  """A tool that looks in config for 'auth.require'. If found and it
  is not None, a login is required and the entry is evaluated as a list of
  conditions that the user must fulfill"""
  conditions = cherrypy.request.config.get('auth.require', None)
  # requested_address = urllib.quote(cherrypy.request.request_line.split()[1])
  if conditions is not None:
    session = getattr(cherrypy, 'session')
    username = session.get(SESSION_KEY, None)
    if username:
      cherrypy.request.login = username
      for condition in conditions:
                # A condition is just a callable that returns true or false
        if not condition():
                    # TODO: log why if possible
          raise cherrypy.HTTPError(403, 'No allowed')
      # TODO: redirect the user to the requested url if the url matches!! -> external view of an event
      # raise cherrypy.HTTPRedirect(requested_address)
    else:
      raise cherrypy.HTTPError(403, 'Not authenticated')


def require(*conditions):
  """
  Decorator that verifies if the user is logged in.
  """

  def decorate(function):
    """A decorator that appends conditions to the auth.require config
    variable."""
    if not hasattr(function, SESSION_CONFIG):
      setattr(function, SESSION_CONFIG, dict())

    attribute = getattr(function, SESSION_CONFIG)
    if 'auth.require' not in attribute:
      attribute['auth.require'] = []
    attribute['auth.require'].extend(conditions)
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
    # should not be done like this :P
    session = getattr(cherrypy, 'session')
    user = session.get(SESSION_USER, None)
    if user:
      return user.permissions.privileged
    else:
      return False
  return check

def groupmanager():
  """
  Condition that verifies if the user has the privileged right set

  Note: Should only be used as condition for the require decorator
  """
  def check():
    """
      Checks if the user has the privileged right
    """
    # should not be done like this :P
    session = getattr(cherrypy, 'session')
    user = session.get(SESSION_USER, None)
    if user:
      return user.permissions.manage_group
    else:
      return False
  return check


def validate():
  def check():
    """
      Checks if the user has the privileged right
    """
    # should not be done like this :P
    session = getattr(cherrypy, 'session')
    user = session.get(SESSION_USER, None)
    if user:
      return user.permissions.validate
    else:
      return False
  return check
