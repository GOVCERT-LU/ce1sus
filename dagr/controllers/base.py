# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for controllers.

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.debug import Log


class ControllerException(Exception):
  """
  Base exception for the controller api
  """
  pass


class SpecialControllerException(ControllerException):
  """
  SpecialControllerException
  """
  pass


class NotImplementedException(ControllerException):
  """
  Not implemented exception
  """
  def __init__(self, message):
    ControllerException.__init__(self, message)


# pylint: disable=R0903
class BaseController:
  """This is the base class for controlles all controllers should extend this
  class"""
  def __init__(self, config):
    self.config = config
    self.logger = Log(self.config)

  def _raise_exception(self, error):
    """
    raises and logs an exception
    """
    raise ControllerException(error)

  def _get_logger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return self.logger.get_logger(self.__class__.__name__)

  def _get_config(self):
    """
    Returns the complete configuration
    """
    return self.config
