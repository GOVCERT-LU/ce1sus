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
                                                  AttributeDefinitionBroker, \
                                                  AttributeDefinition
from ce1sus.brokers.definition.handlerdefinitionbroker import AttributeHandlerBroker
from dagr.db.broker import BrokerException, \
                          ValidationException, \
                          IntegrityException
import types as types
from dagr.controllers.base import SpecialControllerException


class AttributeController(Ce1susBaseController):
  """Controller handling all the requests for attributes"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.attribute_broker = self.broker_factory(AttributeDefinitionBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)

  def get_all_attribute_definitions(self):
    try:
      return self.attribute_broker.get_all(AttributeDefinition.name.asc())
    except BrokerException as error:
      self._raise_exception(error)

  def get_attribute_definitions_by_id(self, object_id):
    try:
      return self.attribute_broker.get_by_id(object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_available_objects(self, attribute):
    try:
      return self.attribute_broker.get_objects_by_attribute(attribute.identifier, False)
    except BrokerException as error:
      self._raise_exception(error)

  @staticmethod
  def __handle_input(add_function, object_id, value):
    if isinstance(value, types.StringTypes):
      add_function(object_id, value, False)
    else:
      for attribute_id in value:
        add_function(object_id, attribute_id, False)

  def modify_object_attribute_relations(self, operation, object_id, remaining_attributes, object_attributes):
    try:
      if operation == 'add':
        AttributeController.__handle_input(self.attribute_broker.add_object_to_attribute,
                                           object_id, remaining_attributes)
      else:
        AttributeController.__handle_input(self.attribute_broker.remove_object_from_attribute,
                                           object_id, object_attributes)
      self.attribute_broker.do_commit(True)
    except IntegrityException as error:
      raise SpecialControllerException(error)
    except BrokerException as error:
      self._raise_exception(error)

  def populate_object(self, identifier=None, name=None, description='',
                      regex='^.*$', class_index=0, action='insert',
                      handler_index=0, share=None, relation=None):
    try:
      return self.attribute_broker.build_attribute_definition(identifier,
                                                              name,
                                                              description,
                                                              regex,
                                                              class_index,
                                                              action,
                                                              handler_index,
                                                              share,
                                                              relation)
    except BrokerException as error:
      self._raise_exception(error)

  def insert_attribute_definition(self, attribute):
    try:
      attribute = self.attribute_broker.insert(attribute)
      return attribute, True
    except ValidationException as error:
      return attribute, False
    except BrokerException as error:
      self._raise_exception(error)

  def update_attribtue_definition(self, attribute):
    try:
      attribute = self.attribute_broker.update(attribute)
      return attribute, True
    except ValidationException as error:
      return attribute, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_attribute_definition(self, attribute):
    try:
      attribute = self.attribute_broker.remove_by_id(attribute.identifier)
      return attribute, False
    except IntegrityException as error:
      raise SpecialControllerException('Cannot delete this attribute. The attribute is still referenced.')
    except BrokerException as error:
      self._raise_exception(error)

  def get_cb_handler_definitions(self):
    try:
      return self.handler_broker.get_all_cb_values()
    except BrokerException as error:
      self._raise_exception(error)

  @staticmethod
  def get_cb_table_definitions(simple=True):
    """ returns the table definitions where the key is the value and value the
    index of the tables.

    Note: Used for displaying the definitions of the tables in combo boxes

    :returns: Dictionary
    """
    return AttributeDefinition.get_cb_values()
