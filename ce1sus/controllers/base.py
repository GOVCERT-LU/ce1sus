# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for controllers.

Created: Jul, 2013
"""
from ce1sus.db.brokers.definitions.objectdefinitionbroker import ObjectDefinitionBroker
from ce1sus.db.brokers.permissions.group import GroupBroker
from ce1sus.db.brokers.permissions.user import UserBroker
from ce1sus.db.classes.user import User
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
  def __init__(self, config):
    self.config = config
    self.__logger = Log(self.config)
    self.session_manager = SessionManager(config)
    self.user_broker = self.broker_factory(UserBroker)
    self.group_broker = self.broker_factory(GroupBroker)
    self.obj_def_broker = self.broker_factory(ObjectDefinitionBroker)

  def broker_factory(self, clazz):
    """
    Instantiates a broker.

    Note: In short sets up the broker in a correct manner with all the
    required settings

    :param clazz: The BrokerClass to be instantiated
    :type clazz: Extension of brokerbase

    :returns: Instance of a broker
    """
    self.logger.debug('Create broker for {0}'.format(clazz))
    return self.session_manager.broker_factory(clazz)

  @property
  def logger(self):
    return self.__logger.get_logger(self.__class__.__name__)

  def set_simple_logging(self, instance, user, insert=False):
    if insert:
      instance.creator_id = user.identifier
      instance.created_at = DatumZait.utcnow()
    instance.modifier_id = user.identifier
    instance.modified_on = DatumZait.utcnow()

  def set_extended_logging(self, instance, user, originating_group, insert=False):
    self.set_simple_logging(instance, user, insert)
    if insert:
      group = user.group
      instance.creator_group = group
      instance.originating_group = originating_group
