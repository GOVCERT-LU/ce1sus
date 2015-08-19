# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""

from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from json import dumps
from uuid import uuid4

from ce1sus.common.classes.cacheobject import CacheObject
from ce1sus.controllers.common.basechanger import BaseChanger, AssemblerException
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.brokers.definitions.typebrokers import AttributeTypeBroker
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.errors.errorbase import ErrorObject, ErrorAttribute
from ce1sus.db.classes.internal.object import Object, RelatedObject
from ce1sus.db.common.broker import NothingFoundException, BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class PseudoCyboxAssembler(BaseChanger):

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
    self.log_object_error(parent, json, error.message)
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
    error_entry.event = observable.event[0]
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

  def assemble_object(self, observable, json, cache_object, set_observable=True):
    if json:
      obj = Object()
      self.set_base(obj, json, cache_object, observable)

      # set definition
      definition = self.get_object_definition(observable, json, cache_object)
      if definition:
        # obj.definition = definition
        obj.definition = definition

        if set_observable:
          obj.observable = [observable]

        rel_objs = json.get('related_objects', None)
        if rel_objs:
          for rel_obj in rel_objs:
            rel_obj_inst = self.assemble_related_object(obj, rel_obj, cache_object)
            obj.related_objects.append(rel_obj_inst)

        attributes = json.get('attributes')
        if attributes:
          for attribute in attributes:
            self.assemble_attribute(obj, attribute, cache_object)

        return obj

  def assemble_related_object(self, obj, json, cache_object):
    if json:
      child_obj_json = json.get('object')
      # TODO: findout why observable is unset afterwards
      # observable = obj.observable[0]
      child_obj = self.assemble_object(obj.parent, child_obj_json, cache_object, set_observable=False)

      # update parent
      related_object = RelatedObject()
      # the properties of the child are the same as for the related object as this is in general only a container
      self.set_base(related_object, json, cache_object, obj)

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

      related_object.parent = obj
      related_object.object = child_obj
      related_object.relationship = json.get('relationship', None)
      if related_object.relationship == 'None':
        related_object.relationship = None
      obj.related_objects.append(related_object)

      return related_object

  def get_attribute_definition(self, json, cache_object):
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
        except NothingFoundException as error:
          raise AssemblerException(error)
        except BrokerException as error:
          raise AssemblerException(error)
        cache_object.seen_attr_defs[uuid] = definition
        return definition
    raise AssemblerException('Could not find a definition in the attribute')

  def __get_handler(self, definition, cache_object):
    handler_instance = definition.handler
    handler_instance.attribute_definitions[definition.chksum] = definition

    # Check if the handler requires additional attribute definitions
    additional_attr_defs_chksums = handler_instance.get_additinal_attribute_chksums()

    if additional_attr_defs_chksums:
      additional_attr_definitions = self.attribute_definition_controller.get_defintion_by_chksums(additional_attr_defs_chksums)
      for additional_attr_definition in additional_attr_definitions:
        handler_instance.attribute_definitions[additional_attr_definition.chksum] = additional_attr_definition

    # Check if the handler requires additional object definitions
    additional_obj_defs_chksums = handler_instance.get_additional_object_chksums()

    if additional_obj_defs_chksums:
      additional_obj_definitions = self.object_definition_controller.get_object_definition_by_chksums(additional_obj_defs_chksums)
      for additional_obj_definition in additional_obj_definitions:
        handler_instance.object_definitions[additional_obj_definition.chksum] = additional_obj_definition

    handler_instance.cache_object = cache_object
    # set conditions
    conditions = self.condition_broker.get_all()
    handler_instance.conditions = conditions

    return handler_instance

  def assemble_attribute(self, obj, json, cache_object):
    """This function will never return an object just the information which element changed"""
    # -1: nothing
    # 0: Attribute
    # 1: Object
    # 2: observable
    changed_on = -1
    if json:
      attribute = Attribute()
      self.set_base(attribute, json, cache_object, obj)
      int_cache_object = CacheObject()
      int_cache_object.set_default()

      definition = self.get_attribute_definition(json, cache_object)
      if definition:
        handler_instance = self.__get_handler(definition, cache_object)
        returnvalues = handler_instance.assemble(obj, json)
        observable = obj.get_observable()
        for returnvalue in returnvalues:
          if isinstance(returnvalue, Observable):
            # make the observable composed and append the observables

            changed_on = max(changed_on, 2)
            if observable.observable_composition:
              observable.observable_composition.observables.append(returnvalue)
            else:
              # create new one
              comp_obs = ObservableComposition()
              self.set_base(comp_obs, json, cache_object, observable)
              comp_obs.observable = observable
              observable.observable_composition = comp_obs

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
              found = False
              for attribute in obj.attributes:
                if (returnvalue.value == attribute.value) and (returnvalue.definition.identifier == attribute.definition.identifier):
                  # log the elemsent
                  self.log_attribute_error(obj, attribute.to_dict(int_cache_object), 'Duplicate value')
                  found = True
              if not found:
                obj.attributes.append(returnvalue)
            else:
              error_message = ObjectValidator.getFirstValidationError(attribute)
              self.log_attribute_error(obj, returnvalue.to_dict(cache_object), error_message)
          else:
            raise ValueError('Return value of attribute handler {0} is not a list of Observable, RelatedObject or Attribute'.format(returnvalue))
    return changed_on

  def get_condition(self, uuid, cache_object):
    definition = cache_object.seen_conditions.get(uuid, None)
    if definition:
      return definition
    else:
      definition = self.condition_broker.get_by_uuid(uuid)
      cache_object.seen_conditions[uuid] = definition
      return definition
