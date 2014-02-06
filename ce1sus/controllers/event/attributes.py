# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                  AttributeDefinitionBroker
from dagr.db.broker import ValidationException, \
BrokerException
from ce1sus.common.handlers.base import HandlerException
from ce1sus.brokers.valuebroker import ValueBroker
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.definition.handlerdefinitionbroker import \
                                                        AttributeHandlerBroker


class AttributesController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.attribute_broker = self.broker_factory(AttributeBroker)
    self.def_attributes_broker = self.broker_factory(AttributeDefinitionBroker)
    self.event_broker = self.broker_factory(EventBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.value_broker = self.broker_factory(ValueBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)

  def get_by_id(self, attribute_id):
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

  def remove_by_id(self, attribute_id):
    """
    Returns an event with the given ID

    :param event_id: identifer of the event
    :type event_id: Integer

    :returns: Event
    """
    try:
      return self.attribute_broker.remove_by_id(attribute_id)
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

  def get_cb_attribute_definitions_by_obj(self, obj):
    try:
      return self.def_attributes_broker.get_cb_values(obj.def_object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_attribute_definition_by_id(self, attribute_defintion_id):
    try:
      return self.def_attributes_broker.get_by_id(attribute_defintion_id)
    except BrokerException as error:
      self._raise_exception(error)

  def insert_attributes(self, user, obj, attribute, additional_attributes):
    try:
      self._get_logger().debug('User {0} inserts attributes on object {1}'.format(user.username,
                                                                                  obj.identifier))
      valid = True
      try:
        self.attribute_broker.insert(attribute, commit=False)
      except ValidationException:
        valid = False
      if not additional_attributes is None:
        for additional_attribute in additional_attributes:
          try:
            additional_attribute.attr_parent_id = attribute.identifier
            self.attribute_broker.insert(additional_attribute, commit=False)
          except ValidationException:
            valid = False
        if valid:
          self.attribute_broker.do_commit(True)
        else:
          self.attribute_broker.do_rollback()
      return attribute, additional_attributes, valid

    except BrokerException as error:
      self._raise_exception(error)

  def __populate_attributes(self, user, obj, definition, action, params, rest=False):
    try:
      if action == 'insert':
        definitions = dict()
        definitions[definition.chksum] = definition
        handler_instance = definition.handler
        # get additional definitions if required
        additional_definitions_chksums = handler_instance.get_additinal_attribute_chksums()
        if additional_definitions_chksums:
          additional_definitions = self.def_attributes_broker.get_defintion_by_chksums(additional_definitions_chksums)
          for additional_definition in additional_definitions:
            definitions[additional_definition.chksum] = additional_definition
        if rest:
          attribute, additional_attributes = handler_instance.process_rest_post(obj,
                                                                             definitions,
                                                                             self._get_user(user.username),
                                                                             params)
        else:
          attribute, additional_attributes = handler_instance.process_gui_post(obj,
                                                                             definitions,
                                                                             self._get_user(user.username),
                                                                             params)
        return attribute, additional_attributes
    except (BrokerException, HandlerException) as error:
      self._raise_exception(error)

  @staticmethod
  def __set_web_attribute(attribute):
    attribute.bit_value.is_web_insert = True
    attribute.bit_value.is_validated = True

  @staticmethod
  def __set_rest_attribute(attribute):
    attribute.bit_value.is_web_insert = True
    attribute.bit_value.is_validated = True

  def populate_web_attributes(self, user, obj, definition_id, action, params):
    try:
      definition = self.def_attributes_broker.get_by_id(definition_id)
      attribute, additional_attributes = self.__populate_attributes(user,
                                                                    obj,
                                                                    definition,
                                                                    action,
                                                                    params)
      # set bit values
      AttributesController.__set_web_attribute(attribute)
      if additional_attributes:
        for additional_attribute in additional_attributes:
          AttributesController.__set_web_attribute(additional_attribute)
      return attribute, additional_attributes
    except BrokerException as error:
      self._raise_exception(error)

  def populate_rest_attributes(self, user, rest_attribute, action):
    try:
      definition = self.def_attributes_broker.get_definition_by_chksum(rest_attribute.definition.chksum)
      attribute, additional_attributes = self.__populate_attributes(user,
                                                                    None,
                                                                    definition,
                                                                    action,
                                                                    rest_attribute)
      # set bit values
      AttributesController.__set_rest_attribute(attribute)
      if additional_attributes:
        for additional_attribute in additional_attributes:
          AttributesController.__set_rest_attribute(additional_attribute)
      return attribute, additional_attributes

    except BrokerException as error:
      self._raise_exception(error)
