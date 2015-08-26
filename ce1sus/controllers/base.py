# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for controllers.

Created: Jul, 2013
"""

from ce1sus.common.classes.cacheobject import CacheObject, MergerCache
from ce1sus.db.brokers.definitions.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.db.brokers.definitions.objectdefinitionbroker import ObjectDefinitionBroker
from ce1sus.db.brokers.permissions.group import GroupBroker
from ce1sus.db.brokers.permissions.user import UserBroker
from ce1sus.db.classes.internal.core import SimpleLoggingInformations
from ce1sus.db.common.broker import BrokerBase
from ce1sus.db.common.session import SessionManager
from ce1sus.helpers.changelogger import ChangeLogger
from ce1sus.helpers.common.debug import Log
from ce1sus.helpers.version import Version


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
    self.changelogger = ChangeLogger(config)

    self.user_broker = self.broker_factory(UserBroker)
    self.group_broker = self.broker_factory(GroupBroker)
    self.obj_def_broker = self.broker_factory(ObjectDefinitionBroker)
    self.attr_def_broker = self.broker_factory(AttributeDefinitionBroker)

  def set_version(self, instance, merger_cache):
    if merger_cache.is_changed_version(instance):
      self.logger.debug('Version already changed')
    else:
      merger_cache.set_changed_version(instance)
      # If the newversion is newer take this one
      if merger_cache.result == 0:
        old_version = instance.version.version
        instance.version.increase_major()
        self.logger.info('{0} {1} property version will be be replaced "{2}" by "{3}" result = 0'.format(instance.get_classname(), instance.uuid, old_version, instance.version.version))

      # If the newversion is newer take this one
      if merger_cache.result == 2:
        old_version = instance.version.version
        instance.version.increase_minor()
        self.logger.info('{0} {1} property version will be be replaced "{2}" by "{3}" result = 2'.format(instance.get_classname(), instance.uuid, old_version, instance.version.version))

      elif merger_cache.result == 1:
        # set the new version
        old_version = instance.version.version
        instance.version.add(merger_cache.version)
        self.logger.info('{0} {1} property version will be be replaced "{2}" by "{3}" result = 1'.format(instance.get_classname(), instance.uuid, old_version, instance.version.version))

  def merge_simple_logging_informations(self, old_instance, new_instance, merger_cache, force_new=False):
    if old_instance:
      self.logger.debug('Changing time stamp on {0}{1} - {2}'.format(old_instance.get_classname(), old_instance.uuid, old_instance.modified_on))

      if new_instance and new_instance.modified_on:
        if old_instance.modified_on < new_instance.modified_on:
          old_instance.modifier = merger_cache.user
          old_instance.modified_on = new_instance.modified_on
          self.logger.debug('using the one from new instance {1} - {0}'.format(new_instance.modified_on, new_instance.get_classname()))
          # TODO: find out why I have to do this?
          self.attr_def_broker.session.merge(old_instance)
          self.attr_def_broker.do_commit(False)
        else:
          self.logger.debug('TS is more up to date {1}{0}'.format(old_instance.modified_on, old_instance.get_classname()))
      else:
        self.logger.debug('Cannot make changes on  is more up to date {1}{0}'.format(old_instance.modified_on, old_instance.get_classname()))

  def insert_set_base(self, instance, cache_object):

    if isinstance(cache_object, CacheObject):
      merge_cache = MergerCache(cache_object)
      merge_cache.result = 2
      self.update_modified(instance, merge_cache)
    else:
      raise ValueError('Not cacheobject')

  def remove_set_base(self, instance, cache_object):
    self.insert_set_base(instance, cache_object)

  def update_set_base(self, instance, cache_object):
    # self.insert_set_base(instance, cache_object)
    # TODO: should be handled by the merger
    pass

  def update_modified(self, old_instance, merge_cache):
    if old_instance:
      if hasattr(old_instance, 'parent'):
        parent = old_instance.parent
        if parent:
          if isinstance(parent, SimpleLoggingInformations):
            self.merge_simple_logging_informations(parent, old_instance, merge_cache, True)
          if hasattr(parent, 'version'):
            self.set_version(parent, merge_cache)
          self.update_modified(parent, merge_cache)

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
