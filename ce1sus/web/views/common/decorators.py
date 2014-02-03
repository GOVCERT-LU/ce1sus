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
import urllib

SESSION_KEY = '_cp_username'
SESSION_CONFIG = '_cp_config'


def check_auth(*args, **kwargs):
  """A tool that looks in config for 'auth.require'. If found and it
  is not None, a login is required and the entry is evaluated as a list of
  conditions that the user must fulfill"""
  conditions = cherrypy.request.config.get('auth.require', None)

  # requested_address = urllib.quote(cherrypy.request.request_line.split()[1])
  if conditions is not None:
    attribute = getattr(cherrypy, 'session')
    username = attribute.get(SESSION_KEY)
    if username:
      cherrypy.request.login = username
      for condition in conditions:
        # A condition is just a callable that returns true or false
        if not condition():
          # TODO: log why if possible
          raise cherrypy.HTTPError(403)
      # TODO: redirect the user to the requested url if the url matches!! -> external view of an event
      # raise cherrypy.HTTPRedirect(requested_address)
    else:
      # redirect in case the session is gone or was not set
      raise cherrypy.HTTPRedirect('/')


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


def require_referer(allowed_referers_list):
  """
  Condition that verifies if the user has the privileged right set

  Note: Should only be used as condition for the require decorator
  """
  def check():
    """
      Checks if the page is accessed from the correct referrer
    """
    referer_parts = cherrypy.request.headers.get('Referer', '/').split('/')
    if len(referer_parts) < 4 or len(referer_parts) > 4:
      return False

    requested_address = referer_parts[3]
    if '/{0}'.format(requested_address) in allowed_referers_list:
      return True
    else:
      return False

  return check
