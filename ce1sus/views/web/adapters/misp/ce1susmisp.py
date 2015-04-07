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
    self.event_controller = EventController(config)
    self.relations_controller = RelationController(config)

  def make_misp_xml(self, event):
    flat_attribtues = self.relations_controller.get_flat_attributes_for_event(event)
    xml_event = self.make_event(event, flat_attribtues)

    return self.wrapper(etree.tostring(xml_event, pretty_print=True))

  def __append_child(self, node, id, value):
    child = etree.Element(id)
    child.text = u'{0}'.format(value)
    node.append(child)

  def make_event(self, event, attributes):
    root = etree.Element('Event')
    self.__append_child(root, 'id', event.identifier)
    self.__append_child(root, 'org', event.creator_group.name)

    self.__append_child(root, 'info', event.description)
    if event.properties.is_shareable:
      published = 1
    else:
      published = 0

    self.__append_child(root, 'published', published)
    self.__append_child(root, 'uuid', event.uuid)
    self.__append_child(root, 'attribute_count', len(attributes))
    self.__append_child(root, 'proposal_email_lock', 0)
    self.__append_child(root, 'orgc', event.originating_group.name)
    self.__append_child(root, 'locked', 0)
    self.__append_child(root, 'publish_timestamp', event.last_publish_date)
    self.__append_child(root, 'analysis', Ce1susMISP.analysis_id_map.get(event.analysis_id, 0))
    self.__append_child(root, 'threat_level_id', Ce1susMISP.threat_level_id_map.get(event.risk_id, 4))
    self.__append_child(root, 'distribution', Ce1susMISP.distribution_to_tlp_map.get(event.tlp_level_id, 2))
    self.__append_child(root, 'ShadowAttribtue', '')
    self.__append_child(root, 'RelatedEvent', '')
    # self.__append_child(root, 'date', event.first_seen.date())
    for attribute in attributes:
      xml_attr = self.__make_attribute(attribute)
      root.append(xml_attr)
    return root

  def get_attr_type(self, attr):
    attr_def_name = attr.definition.name
    if attr_def_name in ['Artifact']:
      return 'attachment'
    elif attr_def_name in ['Artifact']:
      return 'comment'
    elif attr_def_name in ['Artifact']:
      return 'domain'
    elif attr_def_name in ['Artifact']:
      return 'email-attachment'
    elif attr_def_name in ['Artifact']:
      return 'email-dst'
    elif attr_def_name in ['Artifact']:
      return 'email-src'
    elif attr_def_name in ['Artifact']:
      return 'email-subject'
    elif attr_def_name in ['Artifact']:
      return 'filename'
    elif attr_def_name in ['Artifact']:
      return 'hostname'
    elif attr_def_name in ['Artifact']:
      return 'http-method'
    elif attr_def_name in ['Artifact']:
      return 'ip-dst'
    elif attr_def_name in ['Artifact']:
      return 'ip-src'
    elif attr_def_name in ['Artifact']:
      return 'link'
    elif attr_def_name in ['Artifact']:
      return 'malware-sample'
    elif attr_def_name in ['Artifact']:
      return 'md5'
    elif attr_def_name in ['Artifact']:
      return 'mutex'
    elif attr_def_name in ['Artifact']:
      return 'named pipe'
    elif attr_def_name in ['Artifact']:
      return 'pattern-in-file'
    elif attr_def_name in ['Artifact']:
      return 'pattern-in-memory'
    elif attr_def_name in ['Artifact']:
      return 'pattern-in-traffic'
    elif attr_def_name in ['Artifact']:
      return 'regkey'
    elif attr_def_name in ['Artifact']:
      return 'sha1'
    elif attr_def_name in ['Artifact']:
      return 'sha256'
    elif attr_def_name in ['Artifact']:
      return 'snort'
    elif attr_def_name in ['Artifact']:
      return 'text'
    elif attr_def_name in ['Artifact']:
      return 'url'
    elif attr_def_name in ['Artifact']:
      return 'user-agent'
    elif attr_def_name in ['Artifact']:
      return 'yara'
    else:
      return 'other'
    # The following do not exists
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

  def get_attr_category(self, attribute):
    obj_def_name = attribute.object.definition.name
    if obj_def_name in ['Artifact']:
      return 'Artifacts dropped'
    elif obj_def_name in ['Artifact']:
      return 'Internal reference'
    elif obj_def_name in ['Artifact']:
      return 'Targeting data'
    elif obj_def_name in ['foo']:
      # does not exist
      return 'Antivirus detection'
    elif obj_def_name in ['Artifact']:
      return 'Payload delivery'
    elif obj_def_name in ['Artifact']:
      return 'Payload installation'
    elif obj_def_name in ['Artifact']:
      return 'Persistence mechanism'
    elif obj_def_name in ['Artifact']:
      return 'Network activity'
    elif obj_def_name in ['Artifact']:
      return 'Payload type'
    elif obj_def_name in ['Artifact']:
      return 'Attribution'
    elif obj_def_name in ['Artifact']:
      return 'External analysis'
    else:
      return 'Other'

  def __make_attribute(self, attribute):
    root = etree.Element('Attribute')
    self.__append_child(root, 'id', attribute.identifier)
    self.__append_child(root, 'timestamp', time.mktime(attribute.modified_on.timetuple()))
    self.__append_child(root, 'type', self.get_attr_type(attribute))
    self.__append_child(root, 'category', self.get_attr_category(attribute))
    if attribute.is_ioc:
      ids = 1
    else:
      ids = 0
    self.__append_child(root, 'to_ids', ids)
    self.__append_child(root, 'uuid', attribute.uuid)
    self.__append_child(root, 'event_id', attribute.object.event_id)
    self.__append_child(root, 'uuid', attribute.uuid)
    # TODO review this
    self.__append_child(root, 'distribution', Ce1susMISP.distribution_to_tlp_map.get(attribute.object.event.tlp_level_id, 2))
    # TODO add comment
    self.__append_child(root, 'comment', '')
    self.__append_child(root, 'value', attribute.value)
    self.__append_child(root, 'ShadowAttribtue', '')
    return root

  def wrapper(self, xml_string):
    return u'<?xml version="1.0" encoding="UTF-8"?>\n<response>{0}<xml_version>2.3.0</xml_version></response>'.format(xml_string)
