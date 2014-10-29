# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 26, 2014
"""
import cherrypy

from ce1sus.helpers.common.debug import Log
from ce1sus.views.web.common.common import create_response
from ce1sus.views.web.common.decorators import SESSION_KEY, SESSION_USER


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class BaseViewException(Exception):
  """
  Base exception for the view api
  """
  pass


class SessionNotFoundException(BaseViewException):
  """
  Not implemented exception
  """
  pass


class BaseView(object):

  def __init__(self, config):
    """
    Creator

    :param config: The configuration for this module
    :type config: Configuration

    :returns: BaseView
    """
    self.config = config
    self.__logger = Log(config)

  @property
  def logger(self):
    return self.__logger.get_logger(self.__class__.__name__)

  def _create_session(self):
    """
    creates a session in cherrypy
    """
    session = self._get_session()
    session.regenerate()
    self.logger.debug('Created a session')

  def _put_to_session(self, key, value):
    """
      puts/sets a key value pair to the session

    :param key: The key for the value
    :type key: object
    :param value: The value for the key
    :type value: object

    """
    session = self._get_session()
    session[key] = value
    self.logger.debug('Set session value {0} for key {1}'.format(value, key))

  def __is_session_key(self, key):
    """
    Checks if the key is existing the session, else raises a SessionNotFoundException

    :param key: The key for the value
    :type key: object

    """
    session = self._get_session()
    if key not in session.keys():
      self.logger.debug('Key {0} is not defined in session'.format(key))
      raise SessionNotFoundException('Key {0} was not defined in session'.format(key))

  def _get_from_session(self, key, default_value=None):
    """
    Get a variable by key from the session

    Note: The variable stays in the session

    :param key: The key for the value
    :type key: object
    :param value: The value for the key
    :type value: object

    :returns: object
    """
    session = self._get_session()
    value = session.get(key, default_value)
    self.logger.debug('Returned session value "{0}" for key "{1}"'.format(value, key))
    return value

  def _pull_from_session(self, key, default_value=None):
    """
    Pulls a variable by key from the session

    Note: The variable is removed from the session

    :param key: The key for the value
    :type key: object
    :param value: The value for the key
    :type value: object

    :returns: object
    """
    session = self._get_session()
    value = session.pop(key, default_value)
    self.logger.debug('Returned session value "{0}" for key "{1}" and removed it'.format(value, key))
    return value

  def _destroy_session(self):
    """
    Destroys a session
    """
    try:
      session = self._get_session()
      session.clear()
      session.delete()
      # session.clean_up()
      self.logger.debug('Session destroyed')
    except:
      pass

  def _get_session(self):
    """
    Returns the session
    """
    session = getattr(cherrypy, 'session')
    self.logger.debug('Session returned')
    return session

  def raise_exception(self, error, log=True):
    if log:
      self.logger.error(error)
    return create_response(error)

  def user_authenticated(self):
    username = self._get_from_session(SESSION_KEY, None)
    return username

  def get_user(self):
    """
    Returns the user from the session

    :returns: User
    """
    user = self._get_from_session(SESSION_USER)
    return user
