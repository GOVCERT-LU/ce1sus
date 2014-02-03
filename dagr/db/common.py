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
  pass


class ConnectorException(SessionManagerException):
  """Broker Instantiation Exception"""
  pass


class BrokerInstantiationException(Exception):
  """Broker Instantiation Exception"""
  pass


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
    return self.get_session()

  @abstractmethod
  def get_session(self):
    """
    Returns the session

    :returns: SessionObject
    """
    raise ConnectorException('Not Implemented')


class Connector(object):
  """
  base class fir connector classes
  """
  def __init__(self, config):
    self.config = config
    self.debug = self.config.get('debug')
    if self.debug == None:
      self.debug = False
    self.protocol = self.config.get('protocol')

  @abstractmethod
  def close(self):
    """
    Closes the session
    """
    raise ConnectorException('Not implemented in {0}'.format(self.__class__.__name__))

  @abstractmethod
  def create_engine(self):
    """
    Returns a new engine
    """
    raise ConnectorException('Not implemented in {0}'.format(self.__class__.__name__))

  @abstractmethod
  def get_direct_session(self):
    """
    Returns the session from the engine
    """
    raise ConnectorException('Not implemented in {0}'.format(self.__class__.__name__))
