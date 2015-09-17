# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""

from ce1sus.controllers.common.assembler.base import BaseAssembler
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader, PackageIntent
from ce1sus.db.classes.cstix.indicator.indicator import Indicator
from ce1sus.controllers.common.assembler.assemble.ccybox.ccybox import CyboxAssembler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StixAssembler(BaseAssembler):

  def __init__(self, config, session=None):
    super(StixAssembler, self).__init__(config, session)
    self.cybox_assembler = self.controller_factory(CyboxAssembler)

  def assemble_stix_header(self, event, json, cache_object):
    instance = STIXHeader()
    self.set_base(instance, json, cache_object, event)
    if json:
      package_intents = json.get('package_intents', None)
      if package_intents:
        for package_intent in package_intents:
          package_intent = self.assemble_package_intent(instance, package_intent, cache_object)
          instance.package_intents.append(package_intent)
      instance.title = json.get('title', None)
      description = json.get('description', None)
      if description:
        description = self.assemble_structured_text(instance, description, cache_object)
        instance.description = description
      short_description = json.get('short_description', None)
      if short_description:
        short_description = self.assemble_structured_text(instance, short_description, cache_object)
        instance.short_description = short_description
      handling = json.get('handling', None)
      if handling:
        handling = self.assemble_handling(instance, handling, cache_object)
        instance.handling = handling

      information_source = json.get('information_source', None)
      if information_source:
        information_source = self.assemble_information_source(instance, information_source, cache_object)
        instance.information_source = information_source
      else:
        # create a new information source
        # TODO: use variable instead of text
        instance.information_source = self.create_information_source(instance, json, cache_object, role='Initial Author')
      return instance

  def assemble_package_intent(self, parent, json, cache_object):
    instance = PackageIntent()
    self.set_base(instance, json, cache_object, parent)
    instance.parent = parent
    if json:
      intent = json.get('intent', None)
      if intent:
        instance.intent = intent
    return instance

  def assemble_indicator(self, parent, json, cache_object):
    indicator = Indicator()
    indicator.parent = parent
    self.set_base(indicator, json, cache_object, parent)
    if json:
      indicator.alternative_id = json.get('alternative_id', None)
      confidence = json.get('confidence', None)
      if confidence:
        # TODO: assemble
        indicator.confidence = self.assemble_confidence(indicator, confidence, cache_object)
      indicator.id_ = json.get('id_', None)
      indicator.idref = json.get('idref', None)
      if not indicator.idref:
        # indicated_ttps
        information_source = json.get('information_source')
        if information_source:
          indicator.information_source = self.assemble_information_source(indicator, information_source, cache_object)
        # killchains
        # likely_impact
        negate = json.get('negate', '')
        if negate != '':
          indicator.negate = negate
        indicator.observable_composition_operator = json.get('observable_composition_operator', 'OR')
        observables = json.get('observables', None)
        if observables:
          for observable in observables:
            observable = self.cybox_assembler.assemble_observable(indicator, observable, cache_object)
            observable.indicator = indicator
            if observable:
              indicator.observables.append(observable)
        producer = json.get('producer', None)
        if producer:
          indicator.producer = self.assemble_information_source(indicator, producer, cache_object)
        # related_campaigns
        # related_indicators
        # sightings
        # TODO: types
        # valid_time_positions
        # version



      return indicator
