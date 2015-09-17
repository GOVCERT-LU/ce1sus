# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 23, 2015
"""
from sqlalchemy.orm.relationships import RelationshipProperty
from uuid import uuid4

from ce1sus.common.classes.cacheobject import MergerCache
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.controllers.common.common import CommonController
from ce1sus.controllers.common.path import PathController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.brokers.definitions.typebrokers import IndicatorTypeBroker
from ce1sus.db.brokers.event.indicatorbroker import IndicatorBroker
from ce1sus.db.brokers.stix.sigthingbroker import SightingBroker
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.cstix.common.vocabs import IndicatorType as VocabIndicatorType
from ce1sus.db.classes.cstix.indicator.indicator import Indicator, IndicatorType
from ce1sus.db.classes.cstix.indicator.valid_time import ValidTime
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.definitions import ObjectDefinition
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.path import Path
from ce1sus.db.common.broker import BrokerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class IndicatorController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    super(IndicatorController, self).__init__(config, session)
    self.indicator_type_broker = self.broker_factory(IndicatorTypeBroker)
    self.relation_controller = self.controller_factory(RelationController)
    self.indicator_broker = self.broker_factory(IndicatorBroker)
    self.observable_controller = self.controller_factory(ObservableController)
    self.common_controller = self.controller_factory(CommonController)
    self.sigthing_broker = self.broker_factory(SightingBroker)
    self.path_controller = self.controller_factory(PathController)

  def get_all(self):
    try:
      return self.indicator_type_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_types(self):
    result = list()
    for key in VocabIndicatorType.get_dictionary().iterkeys():
      it = IndicatorType()
      it.type = key
      result.append(it)
    return result
  
  def remove_sighting(self, sighting, cache_object, commit=True):
    try:
      self.common_controller.remove_path(sighting.path, cache_object, False)
      if sighting.source and not isinstance(sighting.source, RelationshipProperty):
        self.common_controller.remove_information_source(sighting.source, cache_object, False)
      if sighting.description and not isinstance(sighting.description, RelationshipProperty):
        self.common_controller.remove_structured_text(sighting.description, cache_object, False)
      if sighting.confidence:
        self.common_controller.remove_confidence(sighting.confidence, cache_object, False)
      if sighting.related_observables:
        raise NotImplemented()
      self.sigthing_broker.remove_by_id(sighting.identifier, False)
      self.sigthing_broker.do_commit(commit)
    except BrokerException as error:
      raise ControllerException(error)
  
  def remove_indicator(self, indicator, cache_object, commit=True):
    try:
      self.remove_set_base(indicator, cache_object)
      self.common_controller.remove_path(indicator.path, cache_object, False)
      if indicator.information_source and not isinstance(indicator.information_source, RelationshipProperty):
        self.common_controller.remove_information_source(indicator.information_source, cache_object, False)
      if indicator.description and not isinstance(indicator.description, RelationshipProperty):
        self.common_controller.remove_structured_text(indicator.description, cache_object, False)
      if indicator.short_description and not isinstance(indicator.short_description, RelationshipProperty):
        self.common_controller.remove_structured_text(indicator.short_description, cache_object, False)

      for observable in indicator.observables:
        self.observable_controller.remove_observable(observable, cache_object, False)
      self.common_controller.remove_handling(indicator.handling, cache_object, False)
      # killchain pahses
      # valid time positions
      # related_indicators
      # related campaigns
      if indicator.sightings:
        for sighting in indicator.sightings:
          self.remove_sighting(sighting, cache_object, commit)
      self.indicator_broker.remove_by_id(indicator.identifier, False)
      self.indicator_broker.do_commit(commit)
      
    except BrokerException as error:
      raise ControllerException(error)

  def get_indicator_type(self, indicator_type_name, attribute):

    type_ = IndicatorType()
    type_.type_ = indicator_type_name
    type_.uuid = uuid4()
    self.set_base(type_, attribute)

    return type_


  def map_indicator(self, attributes, indicator_type, event, cache_object):
    # TODO review This

    merger_cache = MergerCache(cache_object)
    merger_cache.insert = True

    if len(attributes) > 0:
      indicator = Indicator()
      indicator.uuid = uuid4()
      self.set_base(indicator, attributes[0])

      # indicator.event = event
      indicator.event_id = event.identifier
      indicator.event = event
      indicator.description = None
      indicator.dbcode = attributes[0].dbcode
      indicator.tlp_level_id = event.tlp_level_id
      indicator.title = 'Indicators for "{0}"'.format(indicator_type)
      indicator.operator = 'OR'
      valid_time_position = ValidTime()
      self.set_base(valid_time_position, attributes[0])
      valid_time_position.start_time = event.modified_on


      if indicator_type and indicator_type != 'Others':
        indicator.types.append(self.get_indicator_type(indicator_type, attributes[0]))

      for attribute in attributes:
        if attribute.is_ioc:

                  # create object
          obj = Object()
          self.set_base(obj, attribute)
          obj.uuid = uuid4()

          obj.definition = ObjectDefinition()
          self.set_base(obj.definition, attribute)
          obj.definition.name = attribute.object.definition.name
          obj.definition.identifier = attribute.object.definition.identifier
          obj.definition.cybox_std = attribute.object.definition.cybox_std

          # create observable
          obs = Observable()
          obs.indicator = indicator
          obs.uuid = uuid4()
          self.set_base(obs, attribute)
          """
          if attribute.object.parent:
            obs.dbcode = attribute.object.parent.dbcode
            obs.tile = attribute.object.parent.title
            obs.description = attribute.object.parent.description
            obs.tlp_level_id = attribute.object.parent.tlp_level_id
          else:
          """
          obs.dbcode = attribute.object.dbcode
          obs.tlp_level_id = attribute.object.tlp_level_id
          obs.object = obj

          obj.observable = obs


          new_attribute = Attribute()
          new_attribute.uuid = uuid4()
          new_attribute.definition = attribute.definition
          new_attribute.object = obj
          new_attribute.value = attribute.value

          self.set_base(new_attribute, attribute)
          obj.attributes.append(new_attribute)

          indicator.observables.append(obs)

      if indicator.observables:
        return indicator

    return None

  def set_base(self, instance, attribute):
    instance.path = Path()
    instance.path.event = attribute.path.event
    instance.creator = attribute.creator
    instance.modifier = attribute.modifier
    instance.creator_group = attribute.creator_group
    instance.created_at = attribute.created_at
    instance.modified_on = attribute.modified_on
    instance.tlp = attribute.tlp
    instance.dbcode = attribute.dbcode
    if hasattr(instance, 'namespace'):
      instance.namespace = 'ce1sus'

  def get_generic_indicators(self, event, cache_object):
    try:
      indicators = list()
      
      flat_attribtues = self.self.path_controller.get_flat_attributes(event, cache_object, True)
      
      mal_email = list()
      ips = list()
      file_hashes = list()
      domains = list()
      urls = list()
      artifacts = list()
      c2s = list()
      others = list()

      # sort attributes
      for attribute in flat_attribtues:
        attr_def_name = attribute.definition.name
        if 'raw' in attr_def_name:
          artifacts.append(attribute)
        elif 'c&c' in attr_def_name:
          c2s.append(attribute)
        elif 'ip' in attr_def_name:
          ips.append(attribute)
        elif attr_def_name in ['md5', 'sha1', 'sha256', 'sha384', 'sha512']:
          file_hashes.append(attribute)
        elif 'email' in attr_def_name:
          mal_email.append(attribute)
        elif 'Domain' in attr_def_name or 'Hostname' in attr_def_name:
          domains.append(attribute)
        elif 'url' in attr_def_name:
          urls.append(attribute)
        else:
          others.append(attribute)

      ind = self.map_indicator(artifacts, 'Malware Artifacts', event, cache_object)

      if ind:
        ind.uuid = uuid4()
        indicators.append(ind)
      ind = self.map_indicator(c2s, 'C2', event, cache_object)
      if ind:
        indicators.append(ind)
      ind = self.map_indicator(ips, 'IP Watchlist', event, cache_object)
      if ind:
        ind.uuid = uuid4()
        indicators.append(ind)
      ind = self.map_indicator(mal_email, 'Malicious E-mail', event, cache_object)
      if ind:
        ind.uuid = uuid4()
        indicators.append(ind)
      ind = self.map_indicator(domains, 'Domain Watchlist', event, cache_object)
      if ind:
        ind.uuid = uuid4()
        indicators.append(ind)
      ind = self.map_indicator(urls, 'URL Watchlist', event, cache_object)
      if ind:
        ind.uuid = uuid4()
        indicators.append(ind)
      ind = self.map_indicator(others, 'Others', event, cache_object)
      if ind:
        ind.uuid = uuid4()
        indicators.append(ind)
      ind = self.map_indicator(file_hashes, 'File Hash Watchlist', event, cache_object)
      if ind:
        ind.uuid = uuid4()
        indicators.append(ind)

      return indicators
    except BrokerException as error:
      self.logger.error(error)
      raise ControllerException(error)
