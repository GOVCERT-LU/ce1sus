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

  def get_all_event_obejcts(self, event, owner, user):
    try:
      if owner:
        return self.object_broker.get_event_objects(event.identifier)
      else:
        return self.get_viewable_event_obejcts(event, user)
    except BrokerException as error:
      self._raise_exception(error)

  def get_viewable_event_obejcts(self, event, user):
    try:
      group_id = user.default_group.identifier
      return self.object_broker.get_viewable_event_objects(event.identifier, group_id)
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

  def populate_web_object(self, identifier, event, parent_object_id, definition_id, user, share, action, proposal):
    try:
      definition = self.def_object_broker.get_by_id(definition_id)
      obj = self.__populate_object(identifier, event.identifier, parent_object_id, definition, user, share, action)
      obj.bit_value.is_web_insert = True
      obj.bit_value.is_validated = not proposal
      obj.bit_value.is_proposal = proposal
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
        obj.event = event
      obj.bit_value.is_validated = False
      obj.bit_value.is_rest_instert = True
      return obj
    except BrokerException as error:
      self._raise_exception(error)

  def insert_object(self, user, event, obj):
    try:
      try:
        user = self._get_user(user.username)
        # only do this when the owner is doing this
        if self.is_event_owner(event, user):
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
        obj.parent_object_id = None
        obj.event_id = None
      else:
        # check if parent objects are connected on the event! else raise an error
        valid = self.__check_if_valid_parent(parent_obj_id, obj.identifier)
        if not valid:
          self._raise_exception('No connection from this object to the event. Please select a different one.')
        obj.parent_object_id = parent_obj_id
        obj.event_id = event.identifier
      self.object_broker.update(obj)
    except BrokerException as error:
      self._raise_exception(error)

  def __check_if_valid_parent(self, parent_obj_id, concernet_obj_id):

    parent_obj = self.object_broker.get_by_id(parent_obj_id)
    if (parent_obj.parent_object_id is None and parent_obj.event_id is None):
      if parent_obj.identifier == concernet_obj_id:
        return False
      else:
        return True
    else:
      if parent_obj.parent_object_id:
        return self.__check_if_valid_parent(parent_obj.parent_object_id, concernet_obj_id)
      else:
        return False

  def get_object_definition_by_id(self, definition_id):
    try:
      return self.def_object_broker.get_by_id(definition_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_flat_objects(self, event, is_owner, user):
    result = list()
    objects = self.object_broker.get_all_event_objects(event.identifier)
    for obj in objects:
      for attribute in obj.attributes:
        if is_owner:
          result.append((obj, attribute))
        else:
          if attribute.creator.default_group.identifier == user.default_group.identifier:
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

  def validate_object_all(self, event, obj, user):
    try:
      obj.bit_value.is_validated = True
      for attribute in obj.attributes:
        attribute.bit_value.is_validated = True
      self.object_broker.update(obj, commit=False)
      if event.published == 1:
        event.published = 0
        self.event_broker.update_event(user, event, commit=False)
      self.object_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)

  def validate_object(self, event, obj, user):
    try:
      obj.bit_value.is_validated = True
      self.object_broker.update(obj, commit=False)
      if event.published == 1:
        event.published = 0
        self.event_broker.update_event(user, event, commit=False)
      self.object_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)
