# -*- coding: utf-8 -*-

"""
Module providing support for the configuration of web applications
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.config import Configuration


class WebConfig(object):
  """The WebConfig class"""

  instance = None

  def __init__(self, configFile, section):
    WebConfig.instance = self
    self.__config = Configuration(configFile, section)

  def get(self, identifier):
    """
    Returns the variable of the configuration file

    :param identifier: The name of the desired configuration
    :type identifier: String

    :returns:
    """
    return self.__config.get(identifier)

  @classmethod
  def getInstance(cls):
    """
    Returns the instance (Singleton pattern)

    :returns: WebConfig
    """
    if WebConfig.instance is None:
      raise IndentationError('No SessionManager present')
    return WebConfig.instance
