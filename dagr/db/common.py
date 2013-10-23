# -*- coding: utf-8 -*-

"""
The base module for common elements of the connectors

Created Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.debug import Log
from abc import abstractmethod


class SessionManagerException(Exception):
  """sessionClazz Manager Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)


class ConnectorException(SessionManagerException):
  """Broker Instantiation Exception"""
  def __init__(self, message):
    SessionManagerException.__init__(self, message)


class BrokerInstantiationException(Exception):
  """Broker Instantiation Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)


# pylint: disable=R0903
class SessionObject(object):
  """
  Session container
  """

  # pylint: disable=R0201
  @property
  def session(self):
    """
    returns the session object
    """
    return self.getSession()

  @abstractmethod
  def getSession(self):
    raise ConnectorException('Not Implemented')


class Connector(object):

  def __init__(self, config):
    self.config = config
    self.debug = self.config.get('debug')
    if self.debug == None:
      self.debug = False
    self.protocol = self.config.get('protocol')

  @abstractmethod
  def open(self):
    raise ConnectorException('Not implemented')

  @abstractmethod
  def close(self):
    raise ConnectorException('Not implemented')

  @abstractmethod
  def getDirectSession(self):
    raise ConnectorException('Not implemented')

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Log.getLogger(self.__class__.__name__)
