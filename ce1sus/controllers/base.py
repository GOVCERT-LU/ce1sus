# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for controllers.

Created: Jul, 2013
"""

from ce1sus.db.brokers.definitions.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.db.brokers.definitions.objectdefinitionbroker import ObjectDefinitionBroker
from ce1sus.db.brokers.permissions.group import GroupBroker
from ce1sus.db.brokers.permissions.user import UserBroker
from ce1sus.db.common.broker import BrokerBase
from ce1sus.db.common.session import SessionManager
from ce1sus.helpers.common.debug import Log


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ControllerException(Exception):
  """
  Base exception for the controller api
  """
  pass


class ControllerIntegrityException(ControllerException):
  pass


class ControllerNothingFoundException(ControllerException):
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
  pass


# pylint: disable=R0903
class BaseController(object):
  """This is the base class for controlles all controllers should extend this
  class"""

  brokers = dict()

  def __init__(self, config, session=None):
    self.config = config
    self.__logger = Log(self.config)
    self.session_manager = SessionManager(config, session)

    self.user_broker = self.broker_factory(UserBroker)
    self.group_broker = self.broker_factory(GroupBroker)
    self.obj_def_broker = self.broker_factory(ObjectDefinitionBroker)
    self.attr_def_broker = self.broker_factory(AttributeDefinitionBroker)

  def broker_factory(self, clazz):
    """
    Instantiates a broker.

    Note: In short sets up the broker in a correct manner with all the
    required settings

    :param clazz: The BrokerClass to be instantiated
    :type clazz: Extension of brokerbase

    :returns: Instance of a broker
    """
    if issubclass(clazz, BrokerBase):

            # need to create the broker

      instance = self.session_manager.broker_factory(clazz)

      return instance

    else:
      raise ControllerException('Class does not implement BrokerBase')

  def get_session(self):
    if self.session:
      return self.session
    else:
      return self.session_manager.connector.get_session()

  @property
  def logger(self):
    return self.__logger.get_logger(self.__class__.__name__)
