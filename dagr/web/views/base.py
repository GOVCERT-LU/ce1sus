# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for controllers.

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.web.helpers.templates import MakoHandler
from dagr.helpers.debug import Log
import cherrypy


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


# pylint: disable=R0903
class BaseView:
  """
  This is the base class for controlles all controllers should extend this
  class
  """
  def __init__(self, config):
    """
    Creator

    :param config: The configuration for this module
    :type config: Configuration

    :returns: BaseView
    """
    self.config = config
    self.mako = MakoHandler(config)
    self.logger = Log(config)

  def _create_session(self):
    """
    creates a session in cherrypy
    """
    session = self._get_session()
    session.regenerate()
    self._get_logger().debug('Created a session')

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
    self._get_logger().debug('Set session value {0} for key {1}'.format(value, key))

  def __is_session_key(self, key):
    """
    Checks if the key is existing the session, else raises a SessionNotFoundException

    :param key: The key for the value
    :type key: object

    """
    session = self._get_session()
    if not key in session.keys():
      self._get_logger().debug('Key {0} is not defined in session'.format(key))
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
    self._get_logger().debug('Returned session value "{0}" for key "{1}"'.format(value, key))
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
    self._get_logger().debug('Returned session value "{0}" for key "{1}" and removed it'.format(value, key))
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
      self._get_logger().debug('Session destroyed')
    except:
      pass

  def _get_session(self):
    """
    Returns the session
    """
    session = getattr(cherrypy, 'session')
    self._get_logger().debug('Session returned')
    return session

  def _get_template(self, template_name):
    """Returns the template

    :param template_name: The name of the template (can also be a path)
    :type template_name: String

    :returns: Template
    """
    return self.mako.get_template(template_name)

  def _render_template(self, template_name, **args):
    """
    Renders a template with the given arguments

    :param template_name: The name of the template (can also be a path)
    :type template_name: String
    :param args: Arguments for the template

    :returns: String
    """
    return self.mako.render_template(template_name, **args)

  def _get_logger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return self.logger.get_logger(self.__class__.__name__)

  def _return_ajax_ok(self):
    """
    Returns the string of an ok for the javascript

    :returns: String
    """
    return '<!--OK--><!-{0}-->'.format(self.__class__.__name__)

  def _return_ajax_post_error(self, message):
    """
    Returns the string of an postError for the javascript

    :returns: String
    """
    return '<!--PostError--><!-{0}-->{1}'.format(self.__class__.__name__, message)

  def _return_ajax_error(self, message):
    """
    Returns the string of an postError for the javascript

    :returns: String
    """
    return '<!--Error--><!-{0}-->{1}'.format(self.__class__.__name__, message)
