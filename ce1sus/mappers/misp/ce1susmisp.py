# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
from lxml import etree
import time

from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.controllers.common.permissions import PermissionController
from ce1sus.controllers.events.event import EventController
from ce1sus.mappers.misp.common import ANALYSIS_MAP, RISK_MAP, DISTRIBUTION_TO_TLP_MAP, MISP_MAP, NOT_MAPPED


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susMISP(BaseController):


  def __init__(self, config, session=None):
    super(Ce1susMISP, self).__init__(config, session)
    self.event_controller = self.controller_factory(EventController)
    self.seen_attributes = list()
    self.permission_controller = self.controller_factory(PermissionController)

  def __append_child(self, node, id_, value):
    child = etree.Element(id_)
    child.text = u'{0}'.format(value)
    node.append(child)

  def create_event_xml(self, event, cache_object):
    # flat_attribtues and references must not contain anything which is not destined to be shared
    xml_event = self.make_event(event, cache_object)
    result = self.wrapper(etree.tostring(xml_event))
    return result

  def get_distribution(self, item):
    distribution = 0
    for key, value in DISTRIBUTION_TO_TLP_MAP.iteritems():
      if value.lower() == item.tlp.lower():
        distribution = key
    return distribution

  def make_event(self, event, cache_object):
    setattr(cache_object, 'counter', 0)
    self.seen_attributes = list()
    root = etree.Element('Event')
    self.__append_child(root, 'id', event.identifier)

    

    self.__append_child(root, 'date', event.created_at.date())
    risk_id = 4
    for key, value in RISK_MAP.iteritems():
      if value.lower() == event.risk.lower():
        risk_id = key
        break
    self.__append_child(root, 'threat_level_id', risk_id)
    if event.stix_header.description:
      self.__append_child(root, 'info', u'{0} - {1}'.format(event.stix_header.title, event.stix_header.description))
    else:
      self.__append_child(root, 'info', u'{0}'.format(event.stix_header.title))
    if event.properties.is_shareable:
      self.__append_child(root, 'published', '1')
    else:
      self.__append_child(root, 'published', '0')
    
    self.__append_child(root, 'uuid', event.uuid)

    analysis_id = 0
    for key, value in ANALYSIS_MAP.iteritems():
      if value.lower() == event.analysis.lower():
        analysis_id = key
        break
    self.__append_child(root, 'analysis', analysis_id)
    self.__append_child(root, 'timestamp', int(time.mktime(event.modified_on.timetuple())))
    self.__append_child(root, 'distribution', self.get_distribution(event))
    self.__append_child(root, 'proposal_email_lock', 0)
    
    self.__append_child(root, 'org', event.creator.group.name)
    self.__append_child(root, 'orgc', event.stix_header.information_source.identity.name)

    self.__append_child(root, 'locked', 0)
    
    if event.last_publish_date:
      self.__append_child(root, 'publish_timestamp', int(time.mktime(event.last_publish_date.timetuple())))
    else:
      self.__append_child(root, 'publish_timestamp', 0)


    self.__append_child(root, 'ShadowAttribtue', '')
    self.__append_child(root, 'RelatedEvent', '')

    # observables
    self.__make_observables(root, event.observables, event.identifier, cache_object)
    # indicators
    self.__make_indicators(root, event.indicators, event.identifier, cache_object)
    # TTP

    # ExploitTarget
    
    #reports
    self.__make_reports(root, event.reports, event.identifier, cache_object)

    self.__append_child(root, 'attribute_count', cache_object.counter)
    return root
  
  def __make_reports(self, root, reports, event_id, cache_object):
    for report in reports:
      if self.permission_controller.is_instance_viewable(report, cache_object):
        self.__make_report(root, report, event_id, cache_object)
  
  def is_reference(self, reference):
    # Remove the comments which are done by the initial misp conversion
    for key in MISP_MAP.iterkeys():
      if reference.value in key:
        self.logger.debug(u'{0} is not a valid reference'.format(reference.value))
        return False
    return True

  def __make_report(self, root, report, event_id, cache_object):
    comment = report.description
    for reference in report.references:
      if self.permission_controller.is_instance_viewable(reference, cache_object) and self.is_reference(reference):
        category, type_ = self.get_category_type('ce1sus-Report', reference)
        if category and type_:
          attr = self.__make_attribute(category, type_, reference, comment, event_id)
          root.append(attr)
          cache_object.counter = cache_object.counter + 1

    for rel_rep in report.related_reports:
      if self.permission_controller.is_instance_viewable(rel_rep, cache_object):
        self.__make_report(root, rel_rep, event_id, cache_object)

  
  def __make_indicators(self, root, indicators, event_id, cache_object):
    #TODO: snort/yara rules
    for indicator in indicators:
      if self.permission_controller.is_instance_viewable(indicator, cache_object):
        self.__make_observables(root, indicator.observables, event_id, cache_object)

  
  def __make_observables(self, root, observables, event_id, cache_object):
    for observable in observables:
      if self.permission_controller.is_instance_viewable(observable, cache_object):
        self.__make_observable(root, observable, event_id, cache_object)


  def __make_observable(self, root, observable, event_id, cache_object):
    if observable.object and self.permission_controller.is_instance_viewable(observable.object, cache_object):
      self.__make_object(root, observable, observable.object, event_id, cache_object)
    if observable.observable_composition and self.permission_controller.is_instance_viewable(observable.observable_composition, cache_object):
      for obs in observable.observable_composition.observables:
        if self.permission_controller.is_instance_viewable(obs, cache_object):
          self.__make_observable(root, obs, event_id, cache_object)
  
  def __map_address(self,attribute):
    attributes = attribute.parent.attributes
    #look for destination or source
    type_ = None
    for attr in attributes:
      if attr.definition.name == 'is_type':
        if attr.value == 'Destination':
          type_ = 'ip-dst'
        else:
          type_ = 'ip-src'
        if type_:
          break
    if type_ is None:
      type_ = 'ip-dst'
    return 'Network activity', type_
  
  def get_category_type(self, prefix, attribute):
    if hasattr(attribute, 'object'):
      objclass = attribute.object.definition.name
    else:
      objclass = 'Reference'
    attr_definition = attribute.definition.name

    search_str = '{2}-{0}-{1}'.format(objclass, attr_definition, prefix)
    if 'Address' in search_str:
      return self.__map_address(attribute)
    
    for key, value in MISP_MAP.iteritems():
      if value == search_str:
        splitted = key.split('/')
        type_ = splitted[1]
        if 'cybox' in value and type_ == 'link':
          type_ = 'url'

        return splitted[0], type_
    if search_str in NOT_MAPPED:
      return None, None
    raise ControllerException(search_str)
  
  def __make_attribute(self, category, type_, attribute, comment, event_id):
    root = etree.Element('Attribute')
    self.__append_child(root, 'id', attribute.identifier)

    if not type_:
      return None
    self.__append_child(root, 'type', type_)
    self.__append_child(root, 'category', category)
    ids = 0
    if hasattr(attribute, 'is_ioc') and attribute.is_ioc:
      ids = 1
    self.__append_child(root, 'to_ids', ids)
    self.__append_child(root, 'uuid', attribute.uuid)
    self.__append_child(root, 'event_id', event_id)
    self.__append_child(root, 'distribution', self.get_distribution(attribute))
    # TODO add comment
    self.__append_child(root, 'timestamp', int(time.mktime(attribute.modified_on.timetuple())))
    if comment:
      self.__append_child(root, 'comment', comment)
    else:
      self.__append_child(root, 'comment', '')
    self.__append_child(root, 'value', attribute.value)
    self.__append_child(root, 'ShadowAttribtue', '')
    return root

  def wrapper(self, xml_string):
    return u'<?xml version="1.0" encoding="UTF-8"?>\n<response>{0}<xml_version>2.3.0</xml_version></response>'.format(xml_string)

  def __make_event(self, event):
    root = etree.Element('Event')
    self.__append_child(root, 'id', event.identifier)
    self.__append_child(root, 'uuid', event.uuid)
    if event.properties.is_shareable:
      value = 1
    else:
      value = 0
    self.__append_child(root, 'published', value)
    self.__append_child(root, 'timestamp', int(time.mktime(event.last_publish_date.timetuple())))
    return root

  def __make_object(self, root, observable, obj, event_id, cache_object):
    if observable.description:
      comment = observable.description.value
    else:
      comment = None
    for attribute in obj.attributes:
      if self.permission_controller.is_instance_viewable(attribute, cache_object) and attribute.value not in self.seen_attributes:
        category, type_ = self.get_category_type('cybox-Observable', attribute)
        if category and type_:
          attr = self.__make_attribute(category, type_, attribute, comment, event_id)
          root.append(attr)
          cache_object.counter = cache_object.counter + 1
          self.seen_attributes.append(attribute.value)
        
    for rel_obj in obj.related_objects:
      if self.permission_controller.is_instance_viewable(rel_obj, cache_object):
        self.__make_object(root, observable, rel_obj, event_id, cache_object)

  def get_reference_category_and_type(self, reference):
    if reference.definition:
      ref_def_name = reference.definition.name
    else:
      ref_def = self.rel_def_broker.get_by_id(reference.definition_id)
      ref_def_name = ref_def.name

    if ref_def_name in ['reference_external_identifier', 'reference_internal_case', 'reference_internal_identifier']:
      return 'Internal reference', 'other'
    elif ref_def_name in ['vulnerability_cve']:
      return 'Payload delivery', 'vulnerability'
    elif ref_def_name in ['link']:
      return 'External analysis', 'link'
    elif ref_def_name in ['comment']:
      return 'External analysis', 'comment'
    else:
      # report file names will no be exported
      return None, None

  def make_index(self, events):
    xml_events_str = ''
    for event in events:
      xml_event = self.__make_event(event)
      xml_event_str = etree.tostring(xml_event)
      xml_events_str = u'{0}\n{1}'.format(xml_events_str, xml_event_str)
    result = self.wrapper(xml_events_str)
    return result
