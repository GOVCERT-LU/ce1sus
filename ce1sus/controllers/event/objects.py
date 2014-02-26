# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from ce1sus.brokers.definition.objectdefinitionbroker import \
                  ObjectDefinitionBroker
from ce1sus.brokers.definition.attributedefinitionbroker import \
                  AttributeDefinitionBroker
from dagr.db.broker import ValidationException, \
BrokerException
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from dagr.helpers.datumzait import DatumZait


class ObjectsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.event_broker = self.broker_factory(EventBroker)
    self.object_broker = self.broker_factory(ObjectBroker)
    self.def_object_broker = self.broker_factory(ObjectDefinitionBroker)
    self.def_attributes_broker = self.broker_factory(AttributeDefinitionBroker)

  def get_attr_def_by_obj_def(self, object_definition):
    """
    Returns a list of attribute definitions with the given object definition

    :param object_definition:
    :type object_definition: ObjectDefinition

    :returns: List of AttributeDefinitions
    """
    try:
      return self.def_attributes_broker.get_cb_values(object_definition.identifier)
    except BrokerException as error:
      self._raise_exception(error)

  def get_object_definition_by_chksum(self, chksum):
    try:
      return self.def_object_broker.get_defintion_by_chksum(chksum)
    except BrokerException as error:
      self._raise_exception(error)

  def get_defintion_by_chksums(self, chksums):
    try:
      return self.def_object_broker.get_defintion_by_chksums(chksums)
    except BrokerException as error:
      self._raise_exception(error)

  def get_cb_object_definitions(self):
    try:
      return self.def_object_broker.get_cb_values()
    except BrokerException as error:
      self._raise_exception(error)

  def get_all_event_obejcts(self, event, owner):
    try:
      if owner:
        return self.object_broker.get_event_objects(event.identifier)
      else:
        return self.get_viewable_event_obejcts(event)
    except BrokerException as error:
      self._raise_exception(error)

  def get_viewable_event_obejcts(self, event):
    try:
      return self.object_broker.get_viewable_event_objects(event.identifier)
    except BrokerException as error:
      self._raise_exception(error)

  def __populate_object(self, identifier, event_id, parent_object_id, definition, user, share, action):
    try:
      if hasattr(user, 'session'):
        user = self._get_user(user.username)
      return self.object_broker.build_object(identifier,
                                            event_id,
                                            definition,
                                            user,
                                            parent_object_id,
                                            shared=share,
                                            action=action)
    except BrokerException as error:
      self._raise_exception(error)

  def populate_web_object(self, identifier, event, parent_object_id, definition_id, user, share, action):
    try:
      definition = self.def_object_broker.get_by_id(definition_id)
      obj = self.__populate_object(identifier, event.identifier, parent_object_id, definition, user, share, action)
      obj.bit_value.is_web_insert = True
      obj.bit_value.is_validated = True
      return obj
    except BrokerException as error:
      self._raise_exception(error)

  def populate_rest_object(self, event, dictinary, parent_object, user, action, obj_defs=dict()):
    try:
      # first get the definition
      definition_dict_obj = dictinary.get('definition', None)
      if definition_dict_obj:
        definition_dict = definition_dict_obj.get('RestObjectDefinition', None)
        if not definition_dict:
          raise BrokerException('No definition specified')
        chksum = definition_dict.get('chksum', None)
        if chksum:
          # check if definition was not already seen
          obj_def = obj_defs.get(chksum, None)
          if obj_def:
            definition = obj_def
          else:
            # TODO: Support auto inserts of definitions
            definition = self.def_object_broker.get_defintion_by_chksum(chksum)
            obj_defs[chksum] = definition
        else:
          raise BrokerException('No chksum specified')
      else:
        raise BrokerException('No definition specified')

      parent_obj_id = None
      if parent_object:
        parent_obj_id = parent_object.identifier

      share = dictinary.get('share', '0')
      obj = self.__populate_object(None, event.identifier, parent_obj_id, definition, user, share, action)

      if parent_object is None:
        obj.event = event
      else:
        parent_object.children.append(obj)
        obj.parent_event = event

      if obj.shared == 1:
        obj.bit_value.is_shareable = True
      else:
        obj.bit_value.is_shareable = False

      obj.bit_value.is_validated = False
      return obj
    except BrokerException as error:
      self._raise_exception(error)

  def insert_object(self, user, event, obj):
    try:
      try:
        user = self._get_user(user.username)
        event.published = 0
        self.event_broker.update_event(user, event, commit=False)
        obj.modified = DatumZait.now()
        self.object_broker.insert(obj, commit=False)
        self.object_broker.do_commit(True)
        return obj, True
      except ValidationException:
        return obj, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_object(self, user, event, obj):
    """
    Removes an object
    """
    try:
      user = self._get_user(user.username)
      self.event_broker.update_event(user, event, commit=False)
      self.object_broker.remove_by_id(obj.identifier, commit=False)
      self.object_broker.do_commit(True)
      return obj, True
    except BrokerException as error:
      self._raise_exception(error)

  def get_cb_event_objects(self, event_id, object_id):
    try:
      return self.object_broker.get_cb_values_object_parents(event_id, object_id)
    except BrokerException as error:
      self._raise_exception(error)

  def set_parent_relation(self, obj, event, parent_obj_id):
    try:
      if parent_obj_id is None:
        obj.event_id = event.identifier
        obj.event = event
        obj.parent_object_id = None
        obj.parent_event_id = None
      else:
        obj.event_id = None
        obj.event = None
        obj.parent_object_id = parent_obj_id
        obj.parent_event_id = event.identifier
      self.object_broker.update(obj)
    except BrokerException as error:
      self._raise_exception(error)

  def get_object_definition_by_id(self, definition_id):
    try:
      return self.def_object_broker.get_by_id(definition_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_flat_objects(self, event, is_owner):
    result = list()
    objects = self.object_broker.get_all_event_objects(event.identifier)
    for obj in objects:
      for attribute in obj.attributes:
        if is_owner:
          result.append((obj, attribute))
        else:
          if attribute.bit_value.is_validated_and_shared:
            result.append((obj, attribute))
    return result

  def get_all_definitions(self):
    try:
      return self.def_object_broker.get_all()
    except BrokerException as error:
      self._raise_exception(error)

  def insert_definition(self, user, attribute_definition):
    try:
      self.def_object_broker.insert(attribute_definition, True)
      return attribute_definition, True
    except ValidationException:
      return attribute_definition, False
    except BrokerException as error:
      self._raise_exception(error)

  def populate_rest_obj_def(self, user, dictionary, action):
    try:
      return self.def_object_broker.build_object_definition(identifier=None, name=dictionary.get('name', None),
                  description=dictionary.get('description', None), action=action,
                               share=dictionary.get('share', None))
    except BrokerException as error:
      self._raise_exception(error)
