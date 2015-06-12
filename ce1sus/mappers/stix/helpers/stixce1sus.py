# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 12, 2014
"""
from datetime import datetime
from uuid import uuid4

from ce1sus.controllers.base import BaseController
from ce1sus.controllers.events.event import EventController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.common import TLP
from ce1sus.db.classes.event import Event
from ce1sus.db.classes.group import Group
from ce1sus.db.classes.indicator import Indicator, Sighting
from ce1sus.mappers.stix.helpers.common import extract_uuid, make_dict_definitions, set_extended_logging, set_properties
from ce1sus.mappers.stix.helpers.cyboxmapper import CyboxMapper
from stix.data_marking import Marking
from stix.extensions.marking.tlp import TLPMarkingStructure


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StixCelsusMapperException(Exception):
  pass


class StixCelsusMapper(BaseController):

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.cybox_mapper = CyboxMapper(config, session)
    self.event_controller = EventController(config, session)
    self.observable_controller = ObservableController(config, session)

  def init(self):
    groups = self.group_broker.get_all()
    self.groups = make_dict_definitions(groups)

  def __convert_info_soucre(self, info_source):
    if info_source and info_source.identity:
      identity = info_source.identity
      identifier = None
      if identity.id_:
        identifier = extract_uuid(identity.id_)
      # check if group exits
      # Only based on the name as the id can vary
      group = self.groups.get(identity.name, None)
      if group:
        return group
      else:
        group = Group()
        if identifier:
          group.uuid = identifier
        else:
          # Unfortenately we must create our own
          group.uuid = uuid4()
        group.name = identity.name
        group.description = u'Auto-generated from STIX'
        group.tlp_lvl = 3
        self.group_broker.insert(group, False)
        self.groups[group.name] = group
      return group
    else:
      return None

  def __convert_sightings(self, sightings, user):
    if sightings:
      if sightings._inner:
        result = list()
        for sighting in sightings._inner:
          ce1sus_sigthing = Sighting()
          ce1sus_sigthing.created_at = sighting.timestamp
          ce1sus_sigthing.timestamp_precision = sighting.timestamp_precision
          ce1sus_sigthing.creator_group = self.__convert_info_soucre(sighting.source)
          ce1sus_sigthing.confidence = sighting.confidence
          ce1sus_sigthing.description = sighting.description
          set_extended_logging(ce1sus_sigthing, user, user.group)
          result.append(ce1sus_sigthing)
          return result
      else:
        return None
    else:
      return None

  def __map_stix_package_header(self, stix_package, user):
    self.init()
    self.cybox_mapper.init()
    event = Event()
    event.uuid = extract_uuid(stix_package.id_)
    # event.uuid = stix_package.id_[-36:]
    stix_header = stix_package.stix_header
    event.title = stix_header.title
    if not event.title:
      event.title = stix_header.short_description
    if not event.title:
      event.title = stix_header.description
    if not event.title:
      event.title = 'Generated via STIX - No title'
    info_source = stix_header.information_source
    event.description = stix_header.description
    if info_source:
      # set information source
      set_extended_logging(event, user, self.__convert_info_soucre(info_source))
    if isinstance(stix_header.handling, Marking):
      # set tlp markings if available
      for specification in stix_header.handling._markings:
        for structure in specification.marking_structures:
          if isinstance(structure, TLPMarkingStructure):
                        # TODO: set desrcption with reference
            event.tlp = structure.color.title()
    if not event.tlp_level_id:
      event.tlp = 'White'

    # first and last seen
    if stix_header.information_source:
      # TODO review this
      time = stix_header.information_source.time
      event.created_at = time.produced_time.value
      if time.received_time:
        event.modified_on = time.received_time.value
      else:
        event.modified_on = event.created_at

      event.first_seen = time.start_time
      event.last_seen = time.end_time

    else:
      # if these values were not set use now
      event.created_at = datetime.utcnow()
      event.modified_on = datetime.utcnow()
      event.first_seen = datetime.utcnow()
      event.last_seen = datetime.utcnow()

    # TODO find a way to add this in stix / read it out
    event.status = 'Confirmed'
    event.analysis = 'Unknown'
    event.risk = 'Undefined'
    event.properties.is_shareable = True
    event.properties.is_rest_instert = True

    if not event.first_seen:
      event.first_seen = event.created_at
    if not event.last_seen:
      event.last_seen = event.modified_on
    return event

  def create_event(self, stix_package, user, ignore_id=False):
    # First process the header
    event = self.__map_stix_package_header(stix_package, user)
    set_properties(event)
    # TODO Make relations
    set_extended_logging(event, user, user.group)
    seen_conditions = dict()
    # First handle observables of the package
    if stix_package.observables:
      for observable in stix_package.observables.observables:
        event.observables.append(self.cybox_mapper.create_observable(observable, event, user, event.tlp_level_id, False, seen_conditions))

    # Then handle indicators
    if stix_package.indicators:
      # process iocs
      for indicator in stix_package.indicators:
        child = self.create_indicator(indicator, event, user)
        if child:
          event.indicators.append(child)
        else:
          raise Exception('None Value')

    # Process incidents
    if stix_package.incidents:
      for incident in stix_package.incidents:
        raise StixCelsusMapperException(u'Incidents are not yet supported')

    if not ignore_id:
      self.event_controller.insert_event(user, event, False, False)

    return event

  def get_tlp_id_from_markings(self, indicator):
    handling = indicator.handling
    if handling:
      markings = handling.markings
      for marking in markings:
        for stucture in marking.marking_structures:
          if isinstance(stucture, TLPMarkingStructure):
            color = stucture.color
            tlp_id = TLP.get_by_value(color.title())
            return tlp_id
    return None

  def create_indicator(self, indicator, event, user):
    ce1sus_indicator = Indicator()
    set_properties(ce1sus_indicator)
    if indicator.id_:
      ce1sus_indicator.uuid = extract_uuid(indicator.id_)
    else:
      ce1sus_indicator.uuid = uuid4()
    ce1sus_indicator.title = indicator.title
    ce1sus_indicator.description = indicator.description
    ce1sus_indicator.originating_group = self.__convert_info_soucre(indicator.producer)
    # TODO: Check if condifdence is in the supported range like Low Hiogh medium or even numbers?!
    ce1sus_indicator.confidence = indicator.confidence

    sightings = self.__convert_sightings(indicator.sightings, user)
    if sightings:
      ce1sus_indicator.sightings = sightings
    # TODO: Add indicator types

    # TODO: markings
    if indicator.kill_chain_phases:
      # TODO: Kill Chains
      pass
    # Note observable is actually observables[0]
    if indicator.observables:
      tlp_id = self.get_tlp_id_from_markings(indicator)
      if tlp_id is None:
        tlp_id = event.tlp_level_id
      for observable in indicator.observables:
        observable = self.cybox_mapper.create_observable(observable, event, user, tlp_id, True)
        if observable:
          observable.event = None
          observable.event_id = None
          ce1sus_indicator.observables.append(observable)
    set_extended_logging(ce1sus_indicator, user, user.group)
    return ce1sus_indicator
