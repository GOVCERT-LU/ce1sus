# -*- coding: utf-8 -*-

"""
module handing the object pages

Created: Aug 26, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from ce1sus.brokers.definition.objectdefinitionbroker import ObjectDefinitionBroker
from dagr.db.broker import IntegrityException, BrokerException, ValidationException
import types
from dagr.controllers.base import ControllerException, SpecialControllerException
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition


class ObjectController(Ce1susBaseController):
  """Controller handling all the requests for objects"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.object_broker = self.broker_factory(ObjectDefinitionBroker)

  def get_all_object_definitions(self):
    try:
      return self.object_broker.get_all(ObjectDefinition.name.asc())
    except BrokerException as error:
      self._raise_exception(error)

  def get_object_definitions_by_id(self, object_id):
    try:
      return self.object_broker.get_by_id(object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_available_attributes(self, obj):
    try:
      return self.object_broker.get_attributes_by_object(obj.identifier, False)
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
        ObjectController.__handle_input(self.object_broker.add_attribute_to_object, object_id, remaining_attributes)
      else:
        ObjectController.__handle_input(self.object_broker.remove_attribute_from_object, object_id, object_attributes)
      self.object_broker.do_commit(True)
    except IntegrityException as error:
      raise SpecialControllerException(error)
    except BrokerException as error:
      self._raise_exception(error)

  def populate_object(self, identifier, name, description, action, share):
    try:
      return self.object_broker.build_object_definition(identifier,
                                                        name,
                                                        description,
                                                        action,
                                                        share)
    except BrokerException as error:
      self._raise_exception(error)

  def insert_object_definition(self, obj):
    try:
      obj = self.object_broker.insert(obj)
      return obj, True
    except ValidationException as error:
      return obj, False
    except BrokerException as error:
      self._raise_exception(error)

  def update_object_definition(self, obj):
    try:
      obj = self.object_broker.update(obj)
      return obj, True
    except ValidationException as error:
      return obj, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_object_definition(self, obj):
    try:
      obj = self.object_broker.remove_by_id(obj.identifier)
      return obj, True
    except IntegrityException as error:
      raise SpecialControllerException('Cannot delete this object. The object is still referenced.')
    except BrokerException as error:
      self._raise_exception(error)
