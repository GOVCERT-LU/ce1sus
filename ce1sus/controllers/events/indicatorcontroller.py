# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 23, 2015
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.brokers.definitions.typebrokers import IndicatorTypeBroker
from ce1sus.db.classes.indicator import IndicatorType, Indicator
from ce1sus.db.classes.object import Object
from ce1sus.db.classes.observables import Observable
from ce1sus.db.common.broker import BrokerException
from ce1sus.db.classes.definitions import ObjectDefinition


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class IndicatorController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
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

  def get_indicator_type(self, indicator_type):

    try:
      type_ = self.indicator_type_broker.get_type_by_name(indicator_type)
      return type_
    except BrokerException as error:
      self.logger.error(error)
      message = u'Indicator type {0} is not defined'.format(indicator_type)
      self.logger.error(message)
      raise ControllerException(message)

  def map_indicator(self, attributes, indicator_type, event, user):
    indicator = Indicator()

    # indicator.event = event
    indicator.event_id = event.identifier
    indicator.event = event
    indicator.dbcode = event.dbcode
    indicator.tlp_level_id = event.tlp_level_id
    indicator.title = 'Indicators for "{0}"'.format(indicator_type)
    indicator.operator = 'OR'
    self.set_extended_logging(indicator, user, user.group, True)

    if indicator_type and indicator_type != 'Others':
      indicator.types.append(self.get_indicator_type(indicator_type))

    for attribute in attributes:
      if attribute.is_ioc:
                # create object
        obj = Object()
        obj.dbcode = attribute.object.dbcode
        obj.tlp_level_id = attribute.object.tlp_level_id
        obj.definition = ObjectDefinition()
        obj.definition.name = attribute.object.definition.name
        obj.definition.identifier = attribute.object.definition.identifier
        obj.definition_id = attribute.object.definition.identifier
        obj.attributes.append(attribute)
        self.set_extended_logging(obj, user, user.group, True)
        # create observable
        obs = Observable()
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
        self.set_extended_logging(obs, user, user.group, True)

        indicator.observables.append(obs)

    if indicator.observables:
      return indicator
    else:
      return None

  def get_generic_indicators(self, event, user):
    try:
      user = self.user_broker.getUserByUserName(user.username)
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
        elif 'ipv' in attr_def_name:
          ips.append(attribute)
        elif 'hash' in attr_def_name:
          file_hashes.append(attribute)
        elif 'email' in attr_def_name:
          mal_email.append(attribute)
        elif 'domain' in attr_def_name or 'hostname' in attr_def_name:
          domains.append(attribute)
        elif 'url' in attr_def_name:
          urls.append(attribute)
        else:
          others.append(attribute)

      ind = self.map_indicator(artifacts, 'Malware Artifacts', event, user)
      if ind:
        indicators.append(ind)
      ind = self.map_indicator(c2s, 'C2', event, user)
      if ind:
        indicators.append(ind)
      ind = self.map_indicator(ips, 'IP Watchlist', event, user)
      if ind:
        indicators.append(ind)
      ind = self.map_indicator(mal_email, 'Malicious E-mail', event, user)
      if ind:
        indicators.append(ind)
      ind = self.map_indicator(domains, 'Domain Watchlist', event, user)
      if ind:
        indicators.append(ind)
      ind = self.map_indicator(urls, 'URL Watchlist', event, user)
      if ind:
        indicators.append(ind)
      ind = self.map_indicator(others, 'Others', event, user)
      if ind:
        indicators.append(ind)
      ind = self.map_indicator(file_hashes, 'File Hash Watchlist', event, user)
      if ind:
        indicators.append(ind)

      return indicators
    except BrokerException as error:
      self.logger.error(error)
      raise ControllerException(error)
