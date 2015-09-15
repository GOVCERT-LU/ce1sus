# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 12, 2014
"""
from ce1sus.helpers.common.objects import get_fields
from lxml import etree
from types import StringType

from ce1sus.controllers.base import BaseController
from ce1sus.controllers.events.event import EventController
from ce1sus.db.classes.cstix.extensions.test_mechanism.yara_test_mechanism import YaraTestMechanism
from ce1sus.db.classes.internal.common import Properties
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.path import Path
from ce1sus.mappers.stix.common import get_fqcn, CLASS_MAP
from ce1sus.mappers.stix.cyboxmapper import CyboxConverter
import cybox
import cybox.utils.idgen
from cybox.utils.nsparser import Namespace
import stix
from stix.common.vocabs import HighMediumLow
from stix.core.stix_package import STIXPackage
import stix.utils.idgen


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

LIST_TYPES = {'cybox.core.observable.Observables': 'observables'}

class StixConverterException(Exception):
  pass


class STIXConverter(BaseController):

  def __init__(self, config, session=None):
    super(STIXConverter, self).__init__(config, session)
    ce1sus_url = config.get('ce1sus', 'baseurl', None)
    if ce1sus_url:
            # Set the namespaces
      cybox.utils.idgen.set_id_namespace(Namespace(ce1sus_url, 'ce1sus'))
      stix.utils.idgen.set_id_namespace({ce1sus_url: 'ce1sus'})
    else:
      raise StixConverterException(u'The base url was not specified in configuration')
    self.cybox_mapper = CyboxConverter(config, session)
  
  def __set_tlp_parent(self, instance, cache_object, color):
    if instance.tlp_level_id is None:
      instance.tlp = color
      if instance.parent:
        self.__set_tlp_parent(instance.parent, cache_object, color)

  def set_tlp(self, instance, cache_object, parent):
    color = instance.color.title()
    parent.tlp = color
    if parent.parent:
      self.__set_tlp_parent(parent.parent, cache_object, color)
    
  
  def convert_stix_xml_string(self, xml_string, cache_object):
    xml = etree.fromstring(xml_string)
    stix_package = STIXPackage.from_xml(xml)
    event = self.map_instance(stix_package, cache_object)


    event.analysis = 'None'
    event.status = 'Confirmed'
    event.risk = 'Unknown'
    event.last_seen = event.modified_on
    event.first_seen = event.created_at
    return event

  def set_base(self, instance, stix_instance, cache_object, parent=None):
    instance.path = Path()
    if parent:
      instance.tlp_level_id = parent.tlp_level_id
      instance.dbcode = parent.dbcode
      instance.parent = parent
      if isinstance(parent, Event):
        instance.path.event = parent
      else:
        instance.path.event = parent.path.event
    if hasattr(stix_instance, 'timestamp'):
      instance.modified_on = stix_instance.timestamp.replace(tzinfo=None)
      instance.created_on = stix_instance.timestamp.replace(tzinfo=None)
    else:
      instance.modified_on = parent.modified_on
      instance.created_on = parent.created_on
    instance.creator_group = cache_object.user.group
    instance.creator = cache_object.user
    instance.modifier = cache_object.user


  def handle_markings(self, instance, cache_object, parent):
    result = list()
    for marking in instance.markings:
      mapped = self.map_instance(marking, cache_object, parent)
      result.append(mapped)
    return result

  def handle_list(self, instance, cache_object, parent):
    result = list()
    for item in instance:
      mapped = self.map_instance(item, cache_object, parent)
      result.append(mapped)
    return result

  def direct_vocab(self, instance, cache_object, parent):
    return instance.value

  def map_object(self, instance, cache_object, parent):
    return self.cybox_mapper.map_object(instance, cache_object, parent)

  def handle_encodedCDATA(self, instance, cache_object, parent):
    value = instance.value
    if isinstance(parent, YaraTestMechanism):
      parent.rule = value

  def handle_vocab_list(self, instance, cache_object, parent=None):
    result = list()
    for item in instance:
      fqcn = get_fqcn(item)
      if fqcn:
        clazz = CLASS_MAP.get(fqcn, None)
        ce1sus_instance = clazz()
        ce1sus_instance.value = item.value
        result.append(ce1sus_instance)
      else:
        raise StixConverterException('Cannot find map for class {0}'.format(fqcn))

    return result



  def map_instance(self, instance, cache_object, parent=None):
    if isinstance(instance, (stix.Entity, stix.TypedList, stix.EntityList)) or isinstance(instance, cybox.Entity):
      fqcn = get_fqcn(instance)
      if fqcn:
        clazz = CLASS_MAP.get(fqcn, None)
        if clazz:
          if isinstance(clazz, StringType):
            return getattr(self, clazz)(instance, cache_object, parent)
          else:
            ce1sus_instance = clazz()
            self.set_base(ce1sus_instance, instance, cache_object, parent)
            fields = get_fields(instance)
            for field in fields:
              value = getattr(instance, field)
              if value:
                if isinstance(value, list):
                  new_value = list()
                  for item in value:
                    new_value.append(self.map_instance(item, cache_object, ce1sus_instance))
                else:
                  new_value = self.map_instance(value, cache_object, ce1sus_instance)
                if new_value:
                  setattr(ce1sus_instance, field, new_value)
            return ce1sus_instance
        else:
          attr_name = LIST_TYPES.get(fqcn, None)
          if attr_name:
            for item in getattr(instance, attr_name):
              getattr(parent, attr_name).append(self.map_instance(item, cache_object, parent))
          else:
            raise StixConverterException('Cannot find map for class {0}'.format(fqcn))
    else:
      return instance
