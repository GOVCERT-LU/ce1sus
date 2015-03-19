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
from ce1sus.helpers.common.datumzait import DatumZait
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
  def __init__(self, message):
    ControllerException.__init__(self, message)


# pylint: disable=R0903
class BaseController:
  """This is the base class for controlles all controllers should extend this
  class"""

  brokers = dict()

  def __init__(self, config, session=None):
    self.config = config
    self.__logger = Log(self.config)
    if session:
      self.session = session
      self.session_manager = None
    else:
      self.session = None
      self.session_manager = SessionManager(config)

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
      classname = clazz.__name__
      if classname in BaseController.brokers:
        return BaseController.brokers[classname]
      # need to create the broker
      self.logger.debug('Create broker for {0}'.format(clazz))
      if self.session:
        instance = clazz(self.session)
      else:
        instance = self.session_manager.broker_factory(clazz)

      BaseController.brokers[classname] = instance
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

  def set_simple_logging(self, instance, user, insert=False):
    # set only if not already set :/
    if insert:
      if not (instance.creator_id or instance.creator):
        instance.creator_id = user.identifier
        instance.creator = user
      if not instance.created_at:
        instance.created_at = DatumZait.utcnow()
    if not (instance.modifier_id or instance.modifier):
      instance.modifier_id = user.identifier
      instance.modifier = user
    if not instance.modified_on:
      instance.modified_on = DatumZait.utcnow()

  def set_extended_logging(self, instance, user, originating_group, insert=False):
    self.set_simple_logging(instance, user, insert)
    if insert:
      if not instance.creator_group:
        instance.creator_group = user.group
      if not instance.originating_group:
        instance.originating_group = originating_group
