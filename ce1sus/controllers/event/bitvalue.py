# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Nov 19, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
import cherrypy
from dagr.db.broker import BrokerException
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.event.eventbroker import EventBroker


class BitValueController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.event_broker = self.broker_factory(EventBroker)

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

  @staticmethod
  def __set_shared(instance, share, validated='1'):

    if share == '1':
      instance.bit_value.is_shareable = True
    else:
      instance.bit_value.is_shareable = False
    if validated == '1':
      instance.bit_value.is_validated = True
    else:
      instance.bit_value.is_validated = False

  def __unshare_object(self, obj):
    obj = self.object_broker.get_by_id(obj_id)
    BitValueController.__set_shared(obj, share, validated)

  def set_object_values(self, user, event, obj_id, share, validated='1'):
    try:
      user = self._get_user(user.username)
      self.event_broker.update_event(user, event, False)
      obj = self.object_broker.get_by_id(obj_id)
      BitValueController.__set_shared(obj, share, validated)

      self.object_broker.update_object(user, obj, commit=False)
      self.object_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)

  def set_attribute_values(self, user, event, attr_id, share, validated='1'):
    try:
      user = self._get_user(user.username)
      self.event_broker.update_event(user, event, False)
      attribute = self.attribute_broker.get_by_id(attr_id)
      self.object_broker.update_object(user, attribute.object, commit=False)
      BitValueController.__set_shared(attribute, share, validated)
      self.attribute_broker.update_attribute(user, attribute, False)
      self.attribute_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)
