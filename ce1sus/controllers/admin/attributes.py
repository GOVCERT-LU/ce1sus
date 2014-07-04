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
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker, AttributeDefinition
from ce1sus.brokers.definition.handlerdefinitionbroker import AttributeHandlerBroker
from dagr.db.broker import BrokerException, ValidationException, IntegrityException
import types as types
from dagr.controllers.base import SpecialControllerException
from dagr.helpers.converters import ObjectConverter
import dagr.helpers.strings as strings
from dagr.helpers.hash import hashSHA1
from dagr.helpers.strings import cleanPostValue


class AttributeController(Ce1susBaseController):
  """Controller handling all the requests for attributes"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.attr_def_broker = self.broker_factory(AttributeDefinitionBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)

  def get_attribute_by_id(self, attribute_id):
    try:
      return self.attr_def_broker.get_by_id(attribute_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_all_attr_defs(self):
    """
    Returns all attribute definitions
    """
    try:
      return self.attr_def_broker.get_all(AttributeDefinition.name.asc())
    except BrokerException as error:
      self._raise_exception(error)

  def get_attr_def_by_id(self, object_id):
    """
    Returns the attribute definition by the given id
    """
    try:
      return self.attr_def_broker.get_by_id(object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_available_objects(self, attribute):
    """
    Returns all no associated objects
    """
    try:
      return self.attr_def_broker.get_objects_by_attribute(attribute.identifier, False)
    except BrokerException as error:
      self._raise_exception(error)

  @staticmethod
  def __handle_input(add_function, object_id, value):
    """
    handles the post values of the list view
    """
    if value:
      if isinstance(value, types.StringTypes):
        add_function(object_id, value, False)
      else:
        for attribute_id in value:
          add_function(object_id, attribute_id, False)

  def modify_object_attribute_relations(self, operation, object_id, remaining_attributes, object_attributes):
    try:
      if operation == 'add':
        AttributeController.__handle_input(self.attr_def_broker.add_object_to_attribute,
                                           object_id, remaining_attributes)
      else:
        AttributeController.__handle_input(self.attr_def_broker.remove_object_from_attribute,
                                           object_id, object_attributes)
      self.attr_def_broker.do_commit(True)
    except IntegrityException as error:
      raise SpecialControllerException(error)
    except BrokerException as error:
      self._raise_exception(error)

  def populate_attribute(self, identifier=None, name=None, description='',
                      regex='^.*$', class_index=0, action='insert',
                      handler_index=0, share=None, relation=None):
    """
    puts an attribute with the data together

    :param identifier: The identifier of the attribute,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the attribute
    :type name: strings
    :param description: The description of this attribute
    :type description: strings
    :param regex: The regular expression to use to verify if the value is
                  correct
    :type regex: strings
    :param class_index: The index of the table to use for storing or getting the
                       attribute actual value
    :type class_index: strings
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: strings

    :returns: AttributeDefinition
    """
    attribute = AttributeDefinition()
    if not action == 'insert':
      attribute = self.attr_def_broker.get_by_id(identifier)
      if attribute.deletable == 0:
        self._raise_exception(u'Attribute cannot be edited or deleted')
    if not action == 'remove':
      if isinstance(name, list):
        name = name[0]
      attribute.name = cleanPostValue(name)
      attribute.description = cleanPostValue(description)
      ObjectConverter.set_integer(attribute, 'class_index', class_index)
      ObjectConverter.set_integer(attribute, 'handler_index', handler_index)
      # collect also the handler
      attribute.attribute_handler = self.handler_broker.get_by_id(attribute.handler_index)
      ObjectConverter.set_integer(attribute, 'relation', relation)
      key = '{0}{1}{2}{3}'.format(attribute.name,
                             attribute.regex,
                             attribute.class_index,
                             attribute.attribute_handler.uuid)
      attribute.chksum = hashSHA1(key)
      trimmed_regex = cleanPostValue(regex)
      if strings.isNotNull(trimmed_regex):
        attribute.regex = trimmed_regex
      else:
        attribute.regex = '^.*$'
      ObjectConverter.set_integer(attribute, 'share', share)
    if action == 'insert':
      attribute.deletable = 1
    return attribute

  def insert_attribute_definition(self, attribute):
    try:
      attribute = self.attr_def_broker.insert(attribute)
      return attribute, True
    except ValidationException as error:
      return attribute, False
    except BrokerException as error:
      self._raise_exception(error)

  def update_attribtue_definition(self, attribute):
    try:
      attribute = self.attr_def_broker.update(attribute)
      return attribute, True
    except ValidationException as error:
      return attribute, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_attribute_definition(self, attribute):
    try:
      attribute = self.attr_def_broker.remove_by_id(attribute.identifier)
      return attribute, True
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
