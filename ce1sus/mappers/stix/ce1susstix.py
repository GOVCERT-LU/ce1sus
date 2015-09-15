# -*- coding: utf-8 -*-

"""
(Description)

Created on 10 Sep 2015
"""
from ce1sus.helpers.common.objects import get_class, get_fields
import re
from types import StringType

from ce1sus.controllers.base import BaseController
from ce1sus.controllers.common.permissions import PermissionController
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.information_source import InformationSourceRole
from ce1sus.db.classes.internal.object import Object
from ce1sus.mappers.stix.common import get_fqcn, CLASS_MAP
from cybox.core.object import Object as CyboxObject
from cybox.common.object_properties import CustomProperties, Property
from ce1sus.controllers.events.indicatorcontroller import IndicatorController
from cybox.objects.custom_object import Custom
from stix.data_marking import Marking, MarkingSpecification
from stix.extensions.marking.tlp import TLPMarkingStructure

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

UNMAPPABLE_FIELDS = ['errors', 'attributes', 'groups', 'parent', 'path', 'modifier', 'modifier_id', 'creator', 'creator_id', 'creator_group', 'creator_group_id', 'reports']

STIX_SPECIAL_MAPPINGS = {InformationSourceRole: 'map_information_source_role',
                         Object: 'map_object'}

SPECIAL_ATTR_MAPPINGS = {'ipv4_addr': 'map_ip_address'
                         }

SPECIAL_ATTR_PROP_MAPPINGS = {'DomainName_Value':'value',
                              'url':'value'}

class Ce1susSTIXException(Exception):
  pass

class Ce1susSTIX(BaseController):


  def __init__(self, config, session=None):
    super(Ce1susSTIX, self).__init__(config, session)
    self.permission_controller = self.controller_factory(PermissionController)
    self.indicator_controller = self.controller_factory(IndicatorController)

  def create_event_xml(self, event, cache_object):
    stix_package = self.map_instance(event, cache_object, None)
    stix_package.version = '1.1.1'
    if not event.indicators:
      indicators = self.indicator_controller.get_generic_indicators(event, cache_object)
      for indicator in indicators:
        stix_indicator = self.map_instance(indicator, cache_object, stix_package)
        stix_package.add_indicator(stix_indicator)
    return stix_package.to_xml()
  
  def __get_class(self, instance):
    for key,value in CLASS_MAP.iteritems():
      if isinstance(value, StringType):
        # Then it is a funct this cannot be handled
        pass
      else:
        if isinstance(instance, value):
          splitted = key.rsplit('.',1)
          return get_class(splitted[0],splitted[1])
    for key, value in STIX_SPECIAL_MAPPINGS.iteritems():
      if isinstance(instance, key):
        return value

    raise Ce1susSTIXException('Could not map {0}'.format(get_fqcn(instance)))

  def map_handling(self, instance):
    handling = Marking()
    marking_specification = MarkingSpecification()
    marking_specification.controlled_structure = "//node() | //@*"
    tlp = TLPMarkingStructure()
    tlp.color = instance.tlp.upper()
    marking_specification.marking_structures.append(tlp)
    handling.add_marking(marking_specification)
    return handling


  def map_instance(self, instance, cache_object, parent=None):
    if self.permission_controller.is_instance_viewable(instance, cache_object):
      clazz = self.__get_class(instance)
      if clazz:
        if isinstance(clazz, StringType):
          getattr(self, clazz)(instance, parent, cache_object)
        else:
          stix_instance = clazz()
          if hasattr(stix_instance, 'handling'):
            stix_instance.handling = self.map_handling(instance)
          fields = get_fields(instance)
          for field in fields:
            if field not in instance._PARENTS and field not in UNMAPPABLE_FIELDS:
              value = getattr(instance, field)
              if value:
                if isinstance(value, Entity):
                  new_value = self.map_instance(value, cache_object, stix_instance)
                elif isinstance(value, list):
                  new_value = list()
                  for item in value:
                    result = self.map_instance(item, cache_object, stix_instance)
                    if result:
                      new_value.append(result)
                else:
                  new_value = value
  
                setattr(stix_instance, field, new_value)
          # workaround
          if hasattr(stix_instance, 'composite_indicator_expression'):
            stix_instance.composite_indicator_expression = None
          return stix_instance
    else:
      return None

  def get_modulename(self, name):
    if name == 'URI':
      return name.lower()
    else:
      return re.sub('(?<!^)(?=[A-Z])', '_', name).lower()
  
  def get_property_name(self, name):
    if name in SPECIAL_ATTR_PROP_MAPPINGS.keys():
      return SPECIAL_ATTR_PROP_MAPPINGS[name]
    else:
      return name.lower()
    
  def create_custom_property(self,attribute):
    prop = Property()
    prop.name = attribute.definition.name
    prop.description = attribute.definition.description
    prop.value = attribute.value
    return prop

  def map_condition(self, instance, attribute):
      if attribute.condition:
        value = attribute.condition.value
      else:
        value = 'Equals'
      
      if hasattr(instance, 'condition'):
        instance.condition = value
      else:
        if hasattr(instance, 'hashes') and instance.hashes:
          for h in instance.hashes:
            if h.type_.value.lower() == attribute.definition.name.lower():
              h.simple_hash_value.condition = value
              h.type_.condition = 'Equals'
              break

  def map_object(self, instance, stix_object, cache_object):
    if self.permission_controller.is_instance_viewable(instance, cache_object):
      # create cybox object
      if instance.definition.cybox_std:
        def_name = instance.definition.name
        clazz = get_class('cybox.objects.{0}_object'.format(self.get_modulename(def_name)), def_name)
        cybox_object = clazz()
        for attribute in instance.attributes:
          if self.permission_controller.is_instance_viewable(attribute, cache_object):
            if attribute.definition.cybox_std:
              attr_def_name = attribute.definition.name
              if attr_def_name in SPECIAL_ATTR_MAPPINGS.keys():
                getattr(self, SPECIAL_ATTR_MAPPINGS[attr_def_name])(attribute, cybox_object, cache_object)
              elif hasattr(cybox_object, self.get_property_name(attr_def_name)):
                setattr(cybox_object, self.get_property_name(attr_def_name), attribute.value)
                self.map_condition(getattr(cybox_object, self.get_property_name(attr_def_name)), attribute)
              else:
                raise Ce1susSTIXException('{0} has not property {1}'.format(def_name, attr_def_name))
            else:
              if not cybox_object.custom_properties:
                cybox_object.custom_properties = CustomProperties()
              cybox_object.custom_properties.append(self.create_custom_property(attribute))
  
            self.map_condition(cybox_object, attribute)
      else:
        cybox_object = Custom()
        cybox_object.custom_name = 'ce1sus:{0}'.format(instance.definition.name)
        cybox_object.description = instance.definition.description
        cybox_object.custom_properties = CustomProperties()
        for attribute in instance.attributes:
          if self.permission_controller.is_instance_viewable(attribute, cache_object):
            cybox_object.custom_properties.append(self.create_custom_property(attribute))
      stix_object.object_ = CyboxObject(cybox_object)

  def map_ip_address(self, instance, stix_object, cache_object):
    if self.permission_controller.is_instance_viewable(instance, cache_object):
      attr_def_name = instance.definition.name
      stix_object.address_value = instance.value
      stix_object.category = attr_def_name.replace('_', '-')

  def map_information_source_role(self, instance, stix_object, cache_object):
    if self.permission_controller.is_instance_viewable(instance, cache_object):
      stix_object.add_role(instance.role)
