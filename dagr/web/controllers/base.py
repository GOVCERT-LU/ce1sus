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
from dagr.db.session import SessionManager
from dagr.web.helpers.config import WebConfig
import re


class BaseControllerException(Exception):
  """
  Base exception for the controller api
  """
  def __init__(self, message):
    Exception.__init__(self, message)


class NotImplementedException(BaseControllerException):
  """
  Not implemented exception
  """
  def __init__(self, message):
    BaseControllerException.__init__(self, message)


class BaseController:
  """This is the base class for controlles all controllers should extend this
  class"""
  def __init__(self):
    self.mako = MakoHandler.getInstance()
    self.logger = Log.getLogger(self.__class__.__name__)
    self.config = WebConfig.getInstance()
    self.sessionManager = SessionManager.getInstance()

  def brokerFactory(self, clazz):
    """
    Instantiates a broker.

    Note: In short sets up the broker in a correct manner with all the
    required settings

    :param clazz: The BrokerClass to be instantiated
    :type clazz: Extension of brokerbase

    :returns: Instance of a broker
    """
    self.logger.debug('Create broker for {0}'.format(clazz))
    return self.sessionManager.brokerFactory(clazz)

  def getTemplate(self, name):
    """Returns the template

    :param name: The name of the template (can also be a path)
    :type name: String

    :returns: Template
    """
    return self.mako.getTemplate(name)

  def clearSession(self):
    """
    Clears the session
    """
    raise NotImplementedException(('{0}.clearSession()'
                                   + ' is not implemented').format(
                                                     self.__class__.__name__))

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Log.getLogger(self.__class__.__name__)

  def returnAjaxOK(self):
    """
    Returns the string of an ok for the javascript

    :returns: String
    """
    return '<!--OK--' + self.__class__.__name__

  def getConfigVariable(self, identifier):
    """
    Returns the variable of the configuration file

    :param identifier: The name of the desired configuration
    :type identifier: String

    :returns:
    """
    return self.config.get(identifier)

  def returnAjaxPostError(self):
    """
    Returns the string of an postError for the javascript

    :returns: String
    """
    return '<!--PostError--><!--' + self.__class__.__name__ + '-->'

  def cleanHTMLCode(self, code):
    code = re.sub(r"(\n|\t)", "", code)
    code = re.sub(r"[ ]{2,}", " ", code)
    return code

