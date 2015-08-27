# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 23, 2015
"""
from datetime import datetime
from uuid import uuid4

from ce1sus.common.classes.cacheobject import MergerCache
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.brokers.definitions.typebrokers import IndicatorTypeBroker
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.cstix.common.vocabs import IndicatorType
from ce1sus.db.classes.cstix.indicator.indicator import Indicator
from ce1sus.db.classes.internal.definitions import ObjectDefinition
from ce1sus.db.classes.internal.object import Object
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
    self.relation_controller = RelationController(config, session)

  def get_all(self):
    try:
      return self.indicator_type_broker.get_all()
    except BrokerException as error:
      raise ControllerException(error)

  def get_all_types(self):
    result = list()
    for key in IndicatorType.get_dictionary().iterkeys():
      it = IndicatorType()
      it.type = key
      result.append(it)
    return result

  def get_indicator_type(self, indicator_type, instance, attr_name, merger_cache):



    type_ = IndicatorType(instance, attr_name)
    type_.name = type_.name

    type_.creator = merger_cache.user
    type_.modifier = merger_cache.user
    type_.creator_group = merger_cache.user.group
    type_.crated_on = datetime.utcnow()
    type_.modified_on = datetime.utcnow()

    return type_


  def map_indicator(self, attributes, indicator_type, event, cache_object):
    indicator = Indicator()
    indicator.uuid = uuid4()
    merger_cache = MergerCache(cache_object)
    merger_cache.insert = True

    indicator.creator = merger_cache.user
    indicator.modifier = merger_cache.user
    indicator.creator_group = merger_cache.user.group
    indicator.crated_on = datetime.utcnow()
    indicator.modified_on = datetime.utcnow()
    indicator.tlp = 'Amber'

    # indicator.event = event
    indicator.event_id = event.identifier
    indicator.event = event
    indicator.description = None
    indicator.dbcode = event.dbcode
    indicator.tlp_level_id = event.tlp_level_id
    indicator.title = 'Indicators for "{0}"'.format(indicator_type)
    indicator.operator = 'OR'
    # self.set_extended_logging(indicator, user, True)

    if indicator_type and indicator_type != 'Others':
      # ndicator.types.append(self.get_indicator_type(indicator_type, merger_cache))
      pass

    for attribute in attributes:
      if attribute.is_ioc:
        attribute.uuid = uuid4()
        attribute.creator = merger_cache.user
        attribute.modifier = merger_cache.user
        attribute.creator_group = merger_cache.user.group
        attribute.crated_on = datetime.utcnow()
        attribute.modified_on = datetime.utcnow()
        attribute.tlp = 'Amber'
                # create object
        obj = Object()

        obj.creator = merger_cache.user
        obj.modifier = merger_cache.user
        obj.creator_group = merger_cache.user.group
        obj.crated_on = datetime.utcnow()
        obj.modified_on = datetime.utcnow()
        obj.tlp = 'Amber'

        obj.uuid = uuid4()
        obj.dbcode = attribute.object.dbcode
        obj.tlp_level_id = attribute.object.tlp_level_id
        obj.definition = ObjectDefinition()
        obj.definition.name = attribute.object.definition.name
        obj.definition.identifier = attribute.object.definition.identifier
        obj.definition_id = attribute.object.definition.identifier
        obj.attributes.append(attribute)
        obj.definition.creator = merger_cache.user
        obj.definition.modifier = merger_cache.user

        # self.set_extended_logging(obj, user, True)
        # create observable
        obs = Observable()

        obs.uuid = uuid4()
        obs.creator = merger_cache.user
        obs.modifier = merger_cache.user
        obs.creator_group = merger_cache.user.group
        obs.crated_on = datetime.utcnow()
        obs.modified_on = datetime.utcnow()
        obs.tlp = 'Amber'

        if attribute.object.parent:
          obs.dbcode = attribute.object.parent.dbcode
          obs.tile = attribute.object.parent.title
          obs.description = attribute.object.parent.description
          obs.tlp_level_id = attribute.object.parent.tlp_level_id
        else:
          obs.dbcode = attribute.object.dbcode
          obs.tlp_level_id = attribute.object.tlp_level_id
        obs.object = obj
        obs.event = event
        # self.set_extended_logging(obs, user, True)

        indicator.observables.append(obs)

    if indicator.observables:
      return indicator
    else:
      return None

  def get_generic_indicators(self, event, cache_object):
    try:
      indicators = list()
      flat_attribtues = self.relation_controller.get_flat_attributes_for_event(event)
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
        elif 'hash' in attr_def_name:
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
