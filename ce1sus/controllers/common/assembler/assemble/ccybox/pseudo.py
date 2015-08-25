# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""

from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from json import dumps
from uuid import uuid4

from ce1sus.common.classes.cacheobject import CacheObject
from ce1sus.controllers.common.assembler.base import BaseAssembler, AssemblerException
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.brokers.definitions.typebrokers import AttributeTypeBroker
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.errors.errorbase import ErrorObject, ErrorAttribute
from ce1sus.db.classes.internal.object import Object, RelatedObject
from ce1sus.db.common.broker import BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class PseudoCyboxAssembler(BaseAssembler):

  def __init__(self, config, session=None):
    super(PseudoCyboxAssembler, self).__init__(config, session)
    self.condition_broker = self.broker_factory(ConditionBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)
    self.value_type_broker = self.broker_factory(AttributeTypeBroker)

  def get_object_definition(self, parent, json, cache_object):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition = json.get('definition', None)
      if definition:
        uuid = definition.get('identifier', None)
    if uuid:
      od = cache_object.seen_obj_defs.get(uuid, None)
      if od:
        return od
      else:
        try:
          definition = self.obj_def_broker.get_by_uuid(uuid)
        except BrokerException as error:
          self.log_object_error(parent, json, error.message)
          return None
        cache_object.seen_obj_defs[uuid] = definition
        return definition
    self.log_object_error(parent, json, 'Object does not contain an object definition')
    return None

  def __log_error(self, parent, json, error_message, clazz):
    error_entry = clazz()
    error_entry.message = error_message
    error_entry.dump = dumps(json)
    error_entry.event = parent.event[0]
    return error_entry


  def log_object_error(self, observable, json, error_message):
    error_entry = ErrorObject()
    error_entry.uuid = u'{0}'.format(uuid4())
    error_entry.message = error_message
    error_entry.dump = dumps(json)
    error_entry.event = observable.event
    error_entry.observable = observable
    self.obj_def_broker.session.add(error_entry)
    self.obj_def_broker.do_commit(True)

  def log_attribute_error(self, obj, json, error_message):
    error_entry = ErrorAttribute()
    error_entry.uuid = u'{0}'.format(uuid4())
    error_entry.message = error_message
    error_entry.dump = dumps(json)
    error_entry.event = obj.event
    error_entry.object = obj
    self.obj_def_broker.session.add(error_entry)
    self.obj_def_broker.do_commit(True)

  def assemble_object(self, parent, json, cache_object, set_observable=True):
    if json:
      obj = Object()
      obj.parent = parent
      self.set_base(obj, json, cache_object, parent)

      # set definition
      definition = self.get_object_definition(parent, json, cache_object)
      if definition:
        # obj.definition = definition
        obj.definition = definition

        rel_objs = json.get('related_objects', None)
        if rel_objs:
          for rel_obj in rel_objs:
            rel_obj_inst = self.assemble_related_object(obj, rel_obj, cache_object)
            if rel_obj_inst:
              obj.related_objects.append(rel_obj_inst)

        attributes = json.get('attributes')
        if attributes:
          for attribute in attributes:
            self.assemble_attribute(obj, attribute, cache_object)

        return obj

  def assemble_related_object(self, obj, json, cache_object):
    if json:
      child_obj_json = json.get('object')

      # update parent
      related_object = RelatedObject()
      # the properties of the child are the same as for the related object as this is in general only a container
      self.set_base(related_object, json, cache_object, obj)
      related_object.parent = obj

      child_obj = self.assemble_object(related_object, child_obj_json, cache_object, set_observable=False)

      # Properties should be the same as the one from the related object except they are not in the json
      if child_obj_json.get('properties', None) is None:
        child_obj.dbcode = related_object.dbcode
      if child_obj_json.get('tlp', None) is None:
        child_obj.tlp_level_id = related_object.tlp_level_id

      # also check the other way round
      if json.get('properties', None) is None:
        related_object.dbcode = child_obj.dbcode
      if json.get('tlp', None) is None:
        related_object.tlp_level_id = child_obj.tlp_level_id


      related_object.object = child_obj
      related_object.relationship = json.get('relationship', None)
      if related_object.relationship == 'None':
        related_object.relationship = None
      obj.related_objects.append(related_object)

      return related_object

  def get_attribute_definition(self, parent, json, cache_object):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition = json.get('definition', None)
      if definition:
        uuid = definition.get('identifier', None)
    if uuid:
      ad = cache_object.seen_attr_defs.get(uuid, None)
      if ad:
        return ad
      else:
        try:
          definition = self.attr_def_broker.get_by_uuid(uuid)
        except BrokerException as error:
          self.log_attribute_error(parent, json, error.message)
          return None
        cache_object.seen_attr_defs[uuid] = definition
        return definition
    self.log_attribute_error(parent, json, 'Attribute does not contain an attribute definition')

  def __get_handler(self, parent, definition, cache_object):
    handler_instance = definition.handler
    handler_instance.attribute_definitions[definition.uuid] = definition

    # Check if the handler requires additional attribute definitions
    additional_attr_defs_uuids = handler_instance.get_additinal_attribute_uuids()

    if additional_attr_defs_uuids:

      for attribute_definition_uuid in additional_attr_defs_uuids:
        json = {'definition_id': attribute_definition_uuid}
        attribute_definition = self.get_attribute_definition(parent, json, cache_object)
        if attribute_definition:
          handler_instance.attribute_definitions[attribute_definition.uuid] = attribute_definition

    # Check if the handler requires additional object definitions
    additional_obj_defs_uuids = handler_instance.get_additional_object_uuids()
    if additional_obj_defs_uuids:
      for additional_obj_defs_uuid in additional_obj_defs_uuids:
        json = {'definition_id': additional_obj_defs_uuid}
        object_definition = self.get_object_definition(parent, json, cache_object)
        if object_definition:
          handler_instance.object_definitions[object_definition.uuid] = object_definition

    handler_instance.cache_object = cache_object
    # set conditions
    conditions = self.condition_broker.get_all()
    handler_instance.conditions = conditions

    return handler_instance

  def assemble_attribute(self, obj, json, cache_object):
    if json:
      int_cache_object = CacheObject()
      int_cache_object.set_default()
      changed_on = -1
      definition = self.get_attribute_definition(obj, json, cache_object)
      if definition:
        handler_instance = self.__get_handler(obj, definition, cache_object)
        returnvalues = handler_instance.assemble(obj, json)
        observable = obj.observable
        if returnvalues:
          for returnvalue in returnvalues:
            if isinstance(returnvalue, Observable):
              # make the observable composed and append the observables
              changed_on = max(changed_on, 2)
              if not hasattr(returnvalue, 'dontchange'):
                if observable.observable_composition:
                  # delink observable
                  returnvalue.delink_parent()
                  observable.observable_composition.observables.append(returnvalue)
                else:
                  # create new one
                  comp_obs = ObservableComposition()
                  self.set_base(comp_obs, json, cache_object, observable)
                  comp_obs.observable = observable
                  observable.observable_composition = comp_obs
    
                  # delink observable
                  returnvalue.delink_parent()
    
                  comp_obs.observables.append(returnvalue)
    
                  obs = Observable()
                  self.set_base(obs, json, cache_object, comp_obs)
                  obs.uuid = u'{0}'.format(uuid4())
    
                  obs.object = observable.object
    
                  observable.object = None
    
                  comp_obs.observables.append(obs)

            elif isinstance(returnvalue, RelatedObject):
              changed_on = max(changed_on, 1)
              # append them to the object
              # TODO find out if they are not already present
              obj.related_objects.append(returnvalue)
            elif isinstance(returnvalue, Attribute):
              changed_on = max(changed_on, 0)
              if returnvalue.validate():
                # append if not already present in object
                obj.attributes.append(returnvalue)
              else:
                error_message = ObjectValidator.getFirstValidationError(returnvalue)
                self.log_attribute_error(obj, returnvalue.to_dict(cache_object), error_message)
            else:
              raise AssemblerException('Return value of attribute handler {0} is not a list of Observable, RelatedObject or Attribute'.format(returnvalue))
        else:
          raise AssemblerException('No values were returned by handler')
    if changed_on == 0:
      # return attributes
      return returnvalues
    elif changed_on == 1:
      # return object as there are related object
      return obj
    elif changed_on == 2:
      return observable
    else:
      raise ValueError('Nothing was generated')


  def get_condition(self, uuid, cache_object):
    definition = cache_object.seen_conditions.get(uuid, None)
    if definition:
      return definition
    else:
      definition = self.condition_broker.get_by_uuid(uuid)
      cache_object.seen_conditions[uuid] = definition
      return definition
