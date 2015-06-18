# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 2, 2015
"""
from lxml import etree
import time

from ce1sus.controllers.base import BaseController
from ce1sus.controllers.events.event import EventController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.controllers.events.events import EventsController
from ce1sus.db.brokers.definitions.referencesbroker import ReferenceDefintionsBroker
from ce1sus.db.brokers.event.reportbroker import ReportBroker


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susMISP(BaseController):

  threat_level_id_map = {'3': '1',  # high
                         '2': '2',  # medium
                         '1': '3',  # low
                         '0': '4',  # None
                         '4': '3'
                         }

  analysis_id_map = {'0': '0',  # Initial
                     '1': '1',  # Opened
                     '2': '0',
                     '4': '0',
                     '3': '2',  # Completed
                     }

  distribution_to_tlp_map = {'0': '1',  # red
                             '1': '2',  # amber
                             '2': '3',  # amber
                             '3': '3'  # green
                             }

  def __init__(self, config, session=None):
    BaseController.__init__(self, config, session)
    self.event_controller = EventController(config, session)
    self.relations_controller = RelationController(config, session)
    self.events_controller = EventsController(config, session)
    self.rel_def_broker = self.broker_factory(ReferenceDefintionsBroker)
    self.report_broker = self.broker_factory(ReportBroker)

  def __append_child(self, node, id_, value):
    child = etree.Element(id_)
    child.text = u'{0}'.format(value)
    node.append(child)

  def create_event_xml(self, event, flat_attribtues, references):
    # flat_attribtues and references must not contain anything which is not destined to be shared
    xml_event = self.make_event(event, flat_attribtues, references)
    result = self.wrapper(etree.tostring(xml_event))
    return result

  def make_event(self, event, attributes, references):
    root = etree.Element('Event')
    self.__append_child(root, 'id', event.identifier)
    if event.creator_group:
      self.__append_child(root, 'org', event.creator_group.name)
    else:
      c_group = self.group_broker.get_by_id(event.creator_group_id)
      self.__append_child(root, 'org', c_group.name)

    self.__append_child(root, 'info', u'{0} - {1}'.format(event.title, event.description))
    if event.properties.is_shareable:
      published = 1
    else:
      published = 0

    self.__append_child(root, 'published', published)
    self.__append_child(root, 'uuid', event.uuid)

    self.__append_child(root, 'proposal_email_lock', 0)

    if event.originating_group:
      self.__append_child(root, 'orgc', event.originating_group.name)
    else:
      group = self.group_broker.get_by_id(event.originating_group_id)
      self.__append_child(root, 'orgc', group.name)

    self.__append_child(root, 'locked', 0)
    if event.last_publish_date:
      self.__append_child(root, 'publish_timestamp', int(time.mktime(event.last_publish_date.timetuple())))
    else:
      self.__append_child(root, 'publish_timestamp', 0)
    self.__append_child(root, 'analysis', Ce1susMISP.analysis_id_map.get(event.analysis_id, 0))
    self.__append_child(root, 'threat_level_id', Ce1susMISP.threat_level_id_map.get(event.risk_id, 4))
    self.__append_child(root, 'distribution', Ce1susMISP.distribution_to_tlp_map.get(event.tlp_level_id, 2))
    self.__append_child(root, 'ShadowAttribtue', '')
    self.__append_child(root, 'RelatedEvent', '')
    self.__append_child(root, 'date', event.created_at.date())
    counter = 0
    for attribute in attributes:
      xml_attr = self.__make_attribute(attribute)
      if xml_attr is not None:
        counter = counter + 1
        root.append(xml_attr)
    if references:
      for reference in references:

        xml_ref = self.__make_reference(reference, event)
        if xml_ref:
          counter = counter + 1
          root.append(xml_ref)

    self.__append_child(root, 'attribute_count', len(attributes) + counter)
    return root

  def get_attr_type(self, category, attribute):
    if attribute.definition:
      attr_def_name = attribute.definition.name
    else:
      attr_def = self.attr_def_broker.get_by_id(attribute.definition_id)
      attr_def_name = attr_def.name
    if category in ['Artifacts dropped'] and attr_def_name in ['Artifact']:
      return 'attachment'
    elif attr_def_name in ['DomainName_Value']:
      return 'domain'
    elif attr_def_name in ['email_attachment_file_name']:
      return 'email-attachment'

    elif category in [''] and attr_def_name in ['Artifact']:
      return 'comment'
    elif attr_def_name in ['email_to']:
      return 'email-dst'
    elif attr_def_name in ['email_from', 'email_sender']:
      return 'email-src'
    elif attr_def_name in ['email_subject']:
      return 'email-subject'
    elif attr_def_name in ['File_Name']:
      return 'filename'
    elif attr_def_name in ['Hostname_Value']:
      return 'hostname'
    elif attr_def_name in ['HTTP_Method']:
      return 'http-method'
    elif attr_def_name in ['ipv4_addr', 'ipv4_net', 'ipv6_addr', 'ipv6_addr']:
      category = 'Network activity'
      if attribute.object.observable.description:
        if 'ource' in attribute.object.observable.description:
          return 'ip-dst'
        else:
          return 'ip-src'
      else:
        return 'ip-dst'
    elif attr_def_name in ['url']:
      return 'url'
    elif attr_def_name in ['is_type', 'content_type', 'File_Extension', 'File_Format', 'file_id', 'mime_type', 'Modified_Time', 'Magic_Number', 'WindowsRegistryKey_Hive', 'Accessed_Time', 'Created_Time', 'Size_In_Bytes', 'Protocol', 'Processor_Family', 'Targeted_Platforms', 'malware_file_type', 'URIType']:
      # attributes which are not supported by misp
      return None
    elif attr_def_name in ['Raw_Artifact']:
      # wont return samples
      return None
      # TODO: set this correct
      return 'malware-sample'
    elif attr_def_name in ['hash_md5']:
      return 'md5'
    elif attr_def_name in ['hash_md5']:
      return 'md5'
    elif attr_def_name in ['hash_sha1']:
      return 'sha1'
    elif attr_def_name in ['hash_sha256']:
      return 'sha256'
    elif attr_def_name in ['hash_sha384', 'hash_sha512']:
      return None
    elif attr_def_name in ['Mutex_name']:
      return 'mutex'
    elif attr_def_name in ['Pipe_Name']:
      return 'named pipe'
    elif attr_def_name in ['pattern-in-file']:
      return 'pattern-in-file'
    elif attr_def_name in ['pattern-in-memory', 'memory']:
      return 'pattern-in-memory'
    elif attr_def_name in ['pattern-in-traffic']:
      return 'pattern-in-traffic'
    elif attr_def_name in ['WindowsRegistryKey_Key']:
      return 'regkey'
    elif attr_def_name in ['hash_sha1']:
      return 'sha1'
    elif attr_def_name in ['hash_sha256']:
      return 'sha256'
    elif attr_def_name in ['snort_rule']:
      category = 'Network activity'
      return 'snort'
    elif attr_def_name in ['User_Agent']:
      return 'user-agent'
    elif attr_def_name in ['yara_rule']:
      # ok there can be more
      category = 'Payload delivery'
      return 'yara'
    else:
      return 'other'
    # The following do not exists
    # TODO: Find a way to implement these or don't
    return 'AS'
    return 'filename|md5'
    return 'filename|sha1'
    return 'filename|sha256'
    return 'regkey|value'
    return 'target-email'
    return 'target-external'
    return 'target-location'
    return 'target-machine'
    return 'target-org'
    return 'target-user'
    return 'vulnerability'

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

  def get_attr_category(self, attribute):
    if attribute.object.definition:
      obj_def_name = attribute.object.definition.name
    else:
      obj_def = self.obj_def_broker.get_by_id(attribute.object.definition_id)
      obj_def_name = obj_def.name
    if obj_def_name in ['Artifact']:
      return 'Artifacts dropped'

    elif obj_def_name in ['SNAFU']:
      # Not supported yet
      return 'Targeting data'
    elif obj_def_name in ['SNAFU']:
      # Not supported yet
      return 'Antivirus detection'
    elif obj_def_name in ['email']:
      return 'Payload delivery'
    elif obj_def_name in ['File']:
      return 'Payload installation'
    elif obj_def_name in ['WindowsRegistryKey']:
      return 'Persistence mechanism'
    elif obj_def_name in ['DomainName', 'Hostname', 'HTTPSession', 'Address', 'URI']:
      return 'Network activity'
    elif obj_def_name in ['SNAFU']:
      # Is not mapped yet
      return 'Payload type'
    else:
      return 'Other'

  def __make_attribute(self, attribute):
    root = etree.Element('Attribute')
    self.__append_child(root, 'id', attribute.identifier)

    category = self.get_attr_category(attribute)
    type_ = self.get_attr_type(category, attribute)
    if not type_:
      return None
    self.__append_child(root, 'type', type_)
    self.__append_child(root, 'category', category)
    if attribute.is_ioc:
      ids = 1
    else:
      ids = 0
    self.__append_child(root, 'to_ids', ids)
    self.__append_child(root, 'uuid', attribute.uuid)
    self.__append_child(root, 'event_id', attribute.object.event_id)
    self.__append_child(root, 'distribution', Ce1susMISP.distribution_to_tlp_map.get(attribute.tlp_level_id, 2))
    # TODO add comment
    self.__append_child(root, 'timestamp', int(time.mktime(attribute.modified_on.timetuple())))
    if attribute.object.observable.description:
      self.__append_child(root, 'comment', attribute.object.observable.description)
    else:
      self.__append_child(root, 'comment', '')
    self.__append_child(root, 'value', attribute.value)
    self.__append_child(root, 'ShadowAttribtue', '')
    return root

  def __make_reference(self, reference, event=None):
    root = etree.Element('Attribute')
    self.__append_child(root, 'id', reference.identifier)
    self.__append_child(root, 'timestamp', int(time.mktime(reference.modified_on.timetuple())))
    category, type_ = self.get_reference_category_and_type(reference)
    if not type_:
      return None
    self.__append_child(root, 'type', type_)
    self.__append_child(root, 'category', category)
    ids = 0
    self.__append_child(root, 'to_ids', ids)
    self.__append_child(root, 'uuid', reference.uuid)
    if reference.report:
      self.__append_child(root, 'event_id', reference.report.event_id)
    else:
      self.__append_child(root, 'event_id', event.identifier)

    # TODO review this
    self.__append_child(root, 'distribution', Ce1susMISP.distribution_to_tlp_map.get(reference.report.event.tlp_level_id, 2))
    # TODO add comment
    if reference.report.description:
      self.__append_child(root, 'comment', reference.report.description)
    else:
      self.__append_child(root, 'comment', '')
    self.__append_child(root, 'value', reference.value)
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

  def make_index(self, events):
    xml_events_str = ''
    for event in events:
      xml_event = self.__make_event(event)
      xml_event_str = etree.tostring(xml_event)
      xml_events_str = u'{0}\n{1}'.format(xml_events_str, xml_event_str)
    result = self.wrapper(xml_events_str)
    return result
