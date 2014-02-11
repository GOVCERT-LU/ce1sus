# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for ce1sus controllers.

Created: 30 Sept, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.controllers.base import BaseController
from ce1sus.brokers.permission.userbroker import UserBroker
from dagr.db.session import SessionManager
from ce1sus.common.checks import check_if_event_is_viewable, check_viewable_message
from dagr.helpers.config import ConfigException
from dagr.controllers.base import ControllerException
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.event.attributebroker import AttributeBroker
from dagr.db.broker import BrokerException


class ControllerNothingFoundException(ControllerException):
  """Raised when nothing can be found"""
  pass


class Ce1susBaseController(BaseController):
  """
  Base for ce1sus controllers
  """
  def __init__(self, config):
    BaseController.__init__(self, config)
    self.session_manager = SessionManager(config)
    self.user_broker = self.broker_factory(UserBroker)
    self.event_broker = self.broker_factory(EventBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.attribute_broker = self.broker_factory(AttributeBroker)

  def _get_user(self, username):
    return self.user_broker.getUserByUserName(username)

  def _raise_nothing_found_exception(self, error):
    """
    raises and logs an exception
    """
    self._get_logger().error(error)
    raise ControllerNothingFoundException(error)

  def _get_config_variable(self, key, default_value=None):
    """
    Returns the value of the configuration by key
    """
    try:
      return self.config.get('ce1sus', key, default_value)
    except ConfigException as error:
      self._raise_exception(error)

  def _is_event_viewable_for_user(self, event, user, cache):
    """
    check if the event can be seen by the user
    :param event:
    :type event: Event
    :param user:
    :type user: User

    :returns: Boolean
    """
    viewable = check_if_event_is_viewable(event, user, cache)
    log_msg = check_viewable_message(viewable, event.identifier, user.username)
    self._get_logger().info(log_msg)
    return viewable

  def is_event_owner(self, event, user):
    if user.privileged == 1:
      return True
    else:
      if user.group_id == event.creator_group_id:
        return True
      else:
        return False

  def broker_factory(self, clazz):
    """
    Instantiates a broker.

    Note: In short sets up the broker in a correct manner with all the
    required settings

    :param clazz: The BrokerClass to be instantiated
    :type clazz: Extension of brokerbase

    :returns: Instance of a broker
    """
    self._get_logger().debug('Create broker for {0}'.format(clazz))
    return self.session_manager.broker_factory(clazz)

  def get_event_by_id(self, event_id):
    """
    Returns an event with the given ID

    :param event_id: identifer of the event
    :type event_id: Integer

    :returns: Event
    """
    try:
      return self.event_broker.get_by_id(event_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_object_by_id(self, object_id):
    """
    Returns an event with the given ID

    :param event_id: identifer of the event
    :type event_id: Integer

    :returns: Event
    """
    try:
      return self.object_broker.get_by_id(object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_attribute_by_id(self, attribute_id):
    """
    Returns an event with the given ID

    :param event_id: identifer of the event
    :type event_id: Integer

    :returns: Event
    """
    try:
      return self.attribute_broker.get_by_id(attribute_id)
    except BrokerException as error:
      self._raise_exception(error)
