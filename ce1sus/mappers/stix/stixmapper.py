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
from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.ccybox.core.observables import Observable, ObservableComposition
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.information_source import InformationSource
from ce1sus.db.classes.cstix.common.kill_chains import KillChainPhaseReference
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader, PackageIntent
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification
from ce1sus.db.classes.cstix.extensions.marking.simple_markings import SimpleMarkingStructure
from ce1sus.db.classes.cstix.extensions.marking.tlp import TLPMarkingStructure
from ce1sus.db.classes.cstix.extensions.test_mechanism.yara_test_mechanism import YaraTestMechanism
from ce1sus.db.classes.cstix.indicator.indicator import Indicator, IndicatorType
from ce1sus.db.classes.cstix.indicator.sightings import Sighting
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.path import Path
from ce1sus.mappers.stix.helpers.ce1susstix import Ce1susStixMapper
from ce1sus.mappers.stix.helpers.stixce1sus import StixCelsusMapper, set_extended_logging
import cybox
import cybox.utils.idgen
from cybox.utils.nsparser import Namespace
import stix
from stix.common.vocabs import HighMediumLow
from stix.core.stix_package import STIXPackage
import stix.utils.idgen
from gdata.calendar import Color
from ce1sus.mappers.stix.cyboxmapper import CyboxConverter
from ce1sus.db.classes.cstix.common.tools import ToolInformation


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def get_fqcn(instance):
  if instance:
    return '{0}.{1}'.format(instance.__module__, instance.__class__.__name__)

# the map maps stix classes to ce1sus classes
CLASS_MAP = {'stix.core.stix_package.STIXPackage': Event,
             'stix.core.stix_header.STIXHeader': STIXHeader,
             'stix.data_marking.Marking': 'handle_markings',
             'stix.common.structured_text.StructuredText': StructuredText,
             'stix.core.stix_package.Indicators': 'handle_list',
             'stix.core.ttps.TTPs': 'handle_list',
             'stix.data_marking._MarkingStructures': 'handle_list',
             'stix.data_marking.MarkingSpecification': MarkingSpecification,
             'stix.extensions.marking.tlp.TLPMarkingStructure': 'set_tlp',
             'stix.extensions.marking.simple_marking.SimpleMarkingStructure': SimpleMarkingStructure,
             'stix.indicator.indicator.Indicator': Indicator,
             'stix.common.information_source.InformationSource': InformationSource,
             'stix.common.identity.Identity': Identity,
             'cybox.common.time.Time': CyboxTime,
             'cybox.common.datetimewithprecision.DateTimeWithPrecision': DateTimeWithPrecision,
             'stix.common.confidence.Confidence': Confidence,
             'stix.common.kill_chains.KillChainPhasesReference': 'handle_list',
             'cybox.core.observable.Observable': Observable,
             'cybox.core.observable.ObservableComposition': ObservableComposition,
             'stix.indicator.indicator.IndicatorTypes': 'handle_vocab_list',
             'stix.indicator.indicator._Observables': 'handle_list',
             'stix.common.vocabs.IndicatorType': IndicatorType,
             'stix.common.vocabs.HighMediumLow': 'direct_vocab',
             'stix.common.kill_chains.KillChainPhaseReference': KillChainPhaseReference,
             'cybox.core.object.Object': 'map_object',
             'stix.indicator.sightings.Sightings': 'handle_list',
             'stix.indicator.sightings.Sighting': Sighting,
             'stix.indicator.test_mechanism.TestMechanisms': 'handle_list',
             'stix.extensions.test_mechanism.yara_test_mechanism.YaraTestMechanism': YaraTestMechanism,
             'stix.common.EncodedCDATA': 'handle_encodedCDATA',
             'stix.core.stix_header._PackageIntents': 'handle_list',
             'stix.common.vocabs.PackageIntent': PackageIntent,
             'cybox.common.tools.ToolInformationList': 'handle_list',
             'cybox.common.tools.ToolInformation': ToolInformation
             }


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
    return event

  def set_base(self, instance, cache_object, parent=None):
    instance.path = Path()
    if parent:
      instance.tlp_level_id = parent.tlp_level_id
      instance.dbcode = parent.dbcode
      instance.parent = parent
      if isinstance(parent, Event):
        instance.path.event = parent
      else:
        instance.path.event = parent.path.event

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
            self.set_base(ce1sus_instance, cache_object, parent)
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
                try:
                  
                  setattr(ce1sus_instance, field, new_value)
                except (TypeError, AttributeError) as error:
                  pass
            return ce1sus_instance
        else:
          raise StixConverterException('Cannot find map for class {0}'.format(fqcn))
    else:
      return instance


class StixMapperException(Exception):
  pass


class StixMapper(BaseController):

  def __init__(self, config, session=None):
    super(StixMapper, self).__init__(config, session)
    self.config = config
    
    self.event_controller = EventController(config, session)
    self.stix_ce1sus_mapper = StixCelsusMapper(config, session)
    self.ce1sus_stix_mapper = Ce1susStixMapper(config, session)




  def map_stix_package(self, stix_package, user, make_insert=True, ignore_id=False):
    event = self.stix_ce1sus_mapper.create_event(stix_package, user, ignore_id)
    set_extended_logging(event, user, user.group)
    if make_insert:
      self.event_controller.insert_event(user, event, True, False)

    return event

  def map_ce1sus_event(self, event, user):
    stix_package = self.ce1sus_stix_mapper.create_stix(event, user)


    return stix_package.to_xml()
