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
from dagr.db.broker import IntegrityException, BrokerException, ValidationException, NothingFoundException
import types
from dagr.controllers.base import SpecialControllerException
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition
from dagr.helpers.converters import ObjectConverter
from dagr.helpers.hash import hashSHA1
from dagr.helpers.strings import cleanPostValue


class ObjectController(Ce1susBaseController):
  """Controller handling all the requests for objects"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)

  def get_all_object_definitions(self):
    try:
      return self.obj_def_broker.get_all(ObjectDefinition.name.asc())
    except BrokerException as error:
      self._raise_exception(error)

  def get_object_definitions_by_id(self, object_id):
    try:
      return self.obj_def_broker.get_by_id(object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_object_definition_by_chksum(self, chksum):
    try:
      return self.obj_def_broker.get_definition_by_chksum(chksum)
    except NothingFoundException as error:
      self._raise_nothing_found_exception(error)
    except BrokerException as error:
      self._raise_exception(error)

  def get_available_attributes(self, obj):
    try:
      return self.obj_def_broker.get_attributes_by_object(obj.identifier, False)
    except BrokerException as error:
      self._raise_exception(error)

  @staticmethod
  def __handle_input(add_function, object_id, value):
    if value:
      if isinstance(value, types.StringTypes):
        add_function(object_id, value, False)
      else:
        for attribute_id in value:
          add_function(object_id, attribute_id, False)

  def modify_object_attribute_relations(self, operation, object_id, remaining_attributes, object_attributes):
    try:
      if operation == 'add':
        ObjectController.__handle_input(self.obj_def_broker.add_attribute_to_object, object_id, remaining_attributes)
      else:
        ObjectController.__handle_input(self.obj_def_broker.remove_attribute_from_object, object_id, object_attributes)
      self.obj_def_broker.do_commit(True)
    except IntegrityException as error:
      raise SpecialControllerException(error)
    except BrokerException as error:
      self._raise_exception(error)

  def populate_object(self, identifier, name, description, action, share):
    """
    puts an object with the data together

    :param identifier: The identifier of the object,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the object
    :type name: String
    :param description: The description of this object
    :type description: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: ObjectDefinition
    """
    obj = ObjectDefinition()
    if not action == 'insert':
      obj = self.obj_def_broker.get_by_id(identifier)
    if not action == 'remove':
      obj.name = cleanPostValue(name)
      obj.description = cleanPostValue(description)
      ObjectConverter.set_integer(obj, 'share', share)
      obj.chksum = hashSHA1(obj.name)
    return obj

  def insert_object_definition(self, obj):
    try:
      obj = self.obj_def_broker.insert(obj)
      return obj, True
    except ValidationException as error:
      return obj, False
    except BrokerException as error:
      self._raise_exception(error)

  def update_object_definition(self, obj):
    try:
      obj = self.obj_def_broker.update(obj)
      return obj, True
    except ValidationException as error:
      return obj, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_object_definition(self, obj):
    try:
      obj = self.obj_def_broker.remove_by_id(obj.identifier)
      return obj, True
    except IntegrityException as error:
      raise SpecialControllerException('Cannot delete this object. The object is still referenced.')
    except BrokerException as error:
      self._raise_exception(error)
