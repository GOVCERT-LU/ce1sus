# -*- coding: utf-8 -*-

"""
(Description)

Created on 7 Sep 2015
"""
from ce1sus.helpers.common.objects import get_fields

from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.controllers.common.path import PathController
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.path import Path
from ce1sus.db.common.broker import BrokerException, NothingFoundException
import cybox


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# not mappable items as they are present twice in the object
NOT_MAPPED = ['File_hashes',
              ]

#Don't know how to map these yet
NOT_MAPPED_SUFFIXES = [
                       'datatype',
                       'default_datatype',
                       'apply_condition',
                       'is_case_sensitive',
                       'delimiter',
                       ]

# if a special mapping is required
MAPED_ATTRIBUTES = {
                    'DomainName_value': 'DomainName_value',
                    'URI_type_': 'URIType',
                    'DomainName_type_': 'DomainType',
                    'Process_name': 'Process_name',
                    'WinHandle_type_': 'WinHandleType',
                    'WinHandle_name': 'WinHandle_name',
                    'WinRegistryKey_key': 'WinRegistryKey_key'
                    }


class CyboxConverterException(Exception):
  pass


class CyboxConverter(BaseController):

  def __init__(self, config, session=None):
    super(CyboxConverter, self).__init__(config, session)
    self.condition_broker = self.broker_factory(ConditionBroker)
    self.path_controller = self.controller_factory(PathController)

  def set_base(self, instance, cache_object, parent=None):
    instance.path = Path()
    if parent:
      instance.tlp_level_id = parent.tlp_level_id
      instance.dbcode = parent.dbcode
      instance.path.event = parent.path.event
      instance.modified_on = parent.modified_on
      instance.created_on = parent.created_on
      instance.creator_group = parent.creator_group
      instance.creator = parent.creator
      instance.modifier = parent.modifier
      cache_object.permission_controller.set_properties_according_to_permisssions(instance, cache_object)



  def get_object_definition(self, instance, cache_object):
    try:
      if hasattr(instance, 'properties'):
        name = instance.properties.__class__.__name__
      else:
        name = instance.__class__.__name__
      definition = cache_object.seen_obj_defs.get(name, None)
      if definition:
        return definition
      else:
        definition = self.obj_def_broker.get_defintion_by_name(name)
        cache_object.seen_obj_defs[name] = definition
        return definition
      return definition
    except NothingFoundException as error:
      raise ControllerException('Object definition "{0}" cannot be found'.format(name))
    except BrokerException as error:
      self.logger.error(error)
      raise ControllerException(error)

  def __sanitize(self, text):
    if text.endswith('_'):
      return text[:-1]
    else:
      return text

  def is_not_mappable(self, identifier):
    for item in NOT_MAPPED_SUFFIXES:
      if identifier.endswith(item):
        return True
    return False
    
  def get_remap(self, name, cybox_sruct):
    remap = MAPED_ATTRIBUTES.get(cybox_sruct, None)
    if remap:
      return remap
    return name

  def get_attribute_definition(self, name, cache_object, cybox_sruct):
    self.logger.debug('Getting attribute definition for {0}'.format(name))
    name = self.__sanitize(name)
    remapped_name = self.get_remap(name, cybox_sruct)
    if self.is_not_mappable(name):
      return None

    try:
      definition = cache_object.seen_attr_defs.get(remapped_name, None)
      if definition:
        return definition
      else:
        definition = self.attr_def_broker.get_defintion_by_name(remapped_name, lower=True)
        cache_object.seen_attr_defs[remapped_name] = definition
        return definition
      return definition
    except NothingFoundException as error:
      raise ControllerException('Attribute Definition "{0}" cannot be found for {1}'.format(remapped_name, cybox_sruct))
    except BrokerException as error:
      self.logger.error(error)
      raise ControllerException(error)

  def get_cybox_structure(self, field, properties, cybox_struct=None):
    if cybox_struct:
      struct = '{0}_{1}'.format(cybox_struct, properties.__class__.__name__)
    else:
      struct = properties.__class__.__name__
    struct = '{0}_{1}'.format(struct, field)
    self.logger.debug('Mapping {0}'.format(struct))
    return struct

  def map_properties(self, properties, cache_object, parent, cybox_struct=None):

    fields = get_fields(properties)
    if not 'value' in fields:
      fields.append('value')

    for field in fields:
      if not field.isupper() and field != 'condition':
        if hasattr(properties, field):
          value = getattr(properties, field)
        else:
          value = None
        if value:
          int_cybox_struct = self.get_cybox_structure(field, properties, cybox_struct)

          if int_cybox_struct in NOT_MAPPED:
            continue

          if isinstance(value, cybox.common.properties.String):
            definition = self.get_attribute_definition(field, cache_object, int_cybox_struct)
            if definition:
              attribute = self.map_attribute(definition, '{0}'.format(value), parent, cache_object)
              parent.attributes.append(attribute)
              
          elif isinstance(value, cybox.EntityList):
            for item in value:
              entity = self.map_entity(None, item, cache_object, parent, int_cybox_struct)
              parent.objects.append(entity)
          elif isinstance(value, cybox.Entity):
            entity = self.map_entity(field, value, cache_object, parent, int_cybox_struct)
            parent.objects.append(entity)
          elif isinstance(value, list):
            for item in value:
              definition = self.get_attribute_definition(field, cache_object, int_cybox_struct)
              if definition:
                attribute = self.map_attribute(definition, '{0}'.format(item), parent, cache_object)
                parent.attributes.append(attribute)
          else:
            definition = self.get_attribute_definition(field, cache_object, int_cybox_struct)
            if definition:
              attribute = self.map_attribute(definition, value, parent, cache_object)
              parent.attributes.append(attribute)

  def map_attribute(self, definition, value, parent, cache_object):
    attribute = Attribute()
    self.set_base(attribute, cache_object, parent=parent)
    attribute.object = parent
    attribute.definition = definition
    attribute.value = value
    if hasattr(value, 'condition'):
      attribute.condition = self.get_condition(value.condition, cache_object)
    return attribute

  def get_condition(self, value, cache_object):
    condition = cache_object.seen_conditions.get(value, None)
    if condition:
      return condition
    else:
      try:
        condition = self.condition_broker.get_condition_by_value(value)
        cache_object.seen_conditions[value] = condition
        return condition
      except BrokerException as error:
        raise CyboxConverterException(error)

  def map_object(self, instance, cache_object, parent):
    obj = Object()
    self.set_base(obj, cache_object, parent=parent)
    obj.id_ = instance.id_
    obj.idref = instance.idref
    obj.observable = parent
    if obj.idref is None:
      definition = self.get_object_definition(instance, cache_object)
      obj.definition = definition
      self.map_properties(instance.properties, cache_object, obj)
    # TODO: map custom properties

    return obj

  def map_entity(self, field, instance, cache_object, parent, cybox_struct=None):
    if isinstance(instance, cybox.common.ObjectProperties):
      # this will get a sub object
      obj = Object()
      obj.parent = parent
      self.set_base(obj, cache_object, parent=parent)
      if hasattr(instance, 'id'):
        obj.id_ = instance.id_
      if hasattr(instance, 'idref'):
        obj.idref = instance.idref
      if obj.idref is None:
        definition = self.get_object_definition(instance, cache_object)
        obj.definition = definition
        self.map_properties(instance, cache_object, obj)
        return obj
    else:
      # in this case it is a special container which normally can be mapped on an attribute
      if field:
        int_cybox_struct = self.get_cybox_structure(field, instance, cybox_struct)
        if int_cybox_struct not in NOT_MAPPED:
          definition = self.get_attribute_definition(field, cache_object, int_cybox_struct)
          if definition:
            attribute = self.map_attribute(definition, '{0}'.format(instance), parent, cache_object)
            parent.attributes.append(attribute)
      else:
        raise CyboxConverterException('Field was not specified')


    pass
