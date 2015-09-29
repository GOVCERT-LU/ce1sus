# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 24, 2015
"""
from ce1sus.helpers.common import strings

from ce1sus.controllers.common.basechanger import BaseChangerException, BaseChanger
from ce1sus.db.classes.ccybox.common.time import CyboxTime
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.information_source import InformationSource, InformationSourceRole
from ce1sus.db.classes.cstix.common.related import RelatedIdentity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.common.tools import ToolInformation
from ce1sus.db.classes.cstix.data_marking import MarkingSpecification, MarkingStructure


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class AssemblerException(BaseChangerException):
  pass


class BaseAssembler(BaseChanger):

  def assemble_confidence(self, parent, json, cache_object):
    instance = Confidence()
    instance.parent = parent
    self.set_base(instance, json, cache_object, parent)
    if json:
      instance.timestamp_precision = json.get('timestamp_precision', None)
      instance.timestamp = json.get('timestamp', None)
      value = json.get('timestamp', None)
      if value:
        instance.value = value

      description = json.get('description', None)
      if description:
        instance.description = self.assemble_structured_text(instance, description, cache_object)
      source = json.get('source', None)
      if source:
        instance.source = self.assemble_information_source(instance, source, cache_object)
      return instance

  def assemble_structured_text(self, parent, json, cache_object):
    instance = StructuredText()

    self.set_base(instance, json, cache_object, parent)
    if json:
      instance.id_ = json.get('id_', None)
      instance.value = json.get('value', None)
      instance.structuring_format = json.get('structuring_format', 'text')
      instance.ordinality = json.get('ordinality', None)
      return instance

  def assemble_information_source(self, parent, json, cache_object):
    instance = InformationSource()
    self.set_base(instance, json, cache_object, parent)
    if json:
      description = json.get('description', None)
      if description:
        description = self.assemble_structured_text(instance, description, cache_object)
        instance.description = description
      identity = json.get('identity', None)
      if identity:
        identity = self.assemble_identity(instance, identity, cache_object)
        instance.identity = identity

      contributing_sources = json.get('contributing_sources', None)
      if contributing_sources:
        for contributing_source in contributing_sources:
          contributing_source = self.assemble_information_source(instance, contributing_source, cache_object)
          instance.contributing_sources.append(contributing_source)
      time = json.get('time', None)
      if time:
        time = self.assemble_cybox_time(instance, time, cache_object)
        instance.time = time
      tools = json.get('tools', None)
      if tools:
        for tool in tools:
          tool = self.assemble_toolinformation(instance, tool, cache_object)
          if tool:
            instance.tools.append(tool)

      roles = json.get('roles', None)
      if roles:
        for role in roles:
          role = self.assemble_information_source_role(instance, role, cache_object)
          if role:
            instance.roles.append(role)
      if instance.identity:
        return instance

  def assemble_identity(self, parent, json, cache_object):
    instance = Identity()
    self.set_base(instance, json, cache_object, parent)
    if json:
      instance.id_ = json.get('id_', None)
      instance.idref = json.get('idref', None)
      if not instance.idref:
        instance.name = json.get('name', None)
      related_identities = json.get('related_identities', None)
      if related_identities:
        for related_identity in related_identities:
          related_identity = self.assemble_related_identity(instance, related_identity, cache_object)
          if related_identity:
            instance.related_identities.append(related_identity)
      return instance

  def assemble_related_identity(self, parent, json, cache_object):
    instance = RelatedIdentity()
    self.set_base(instance, json, cache_object, parent)
    if json:
      identity = json.get('item', None)
      if identity:
        self.set_base(instance, json, cache_object, parent)
        identity = self.assemble_identity(instance, identity, cache_object)
        instance.item = identity
        return instance

  def assemble_datetimewithprecision(self, parent, json, cache_object):
    instance = DateTimeWithPrecision()
    self.set_base(instance, json, cache_object, parent)
    if json:
      value = json.get('value', None)
      if value:
        value = strings.stringToDateTime(value)
        instance.value = value
      instance.precision = json.get('precision', 'second')
      return instance

  def assemble_cybox_time(self, parent, json, cache_object):
    instance = CyboxTime()
    self.set_base(instance, json, cache_object, parent)
    if json:
      start_time = json.get('start_time', None)
      if start_time:
        start_time = self.assemble_datetimewithprecision(instance, json, cache_object)
        instance.start_time = start_time
      end_time = json.get('end_time', None)
      if end_time:
        end_time = self.assemble_datetimewithprecision(instance, json, cache_object)
        instance.end_time = end_time
      produced_time = json.get('produced_time', None)
      if produced_time:
        produced_time = self.assemble_datetimewithprecision(instance, json, cache_object)
        instance.start_time = produced_time
      received_time = json.get('received_time', None)
      if received_time:
        received_time = self.assemble_datetimewithprecision(instance, json, cache_object)
        instance.start_time = received_time
      return instance

  def assemble_handling(self, parent, json, cache_object):
    result = list()
    if json:
      for markin_specification in json:
        markin_specification = self.assemble_marking_specification(parent, markin_specification, cache_object)
        if markin_specification:
          result.append(markin_specification)
      return result

  def assemble_marking_specification(self, parent, json, cache_object):
    instance = MarkingSpecification()
    self.set_base(instance, json, cache_object, parent)
    if json:
      instance.id_ = json.get('id_', None)
      instance.version = json.get('version', None)
      instance.controlled_structure = json.get('controlled_structure', None)
      marking_structures = json.get('marking_structures', list())
      for marking_structure in marking_structures:
        marking_structure = self.assemble_marking_structure(instance, marking_structure, cache_object)
        if marking_structure:
          instance.marking_structures.append(marking_structure)

      information_source = json.get('information_source', None)
      if information_source:
        information_source = self.assemble_information_source(instance, information_source, cache_object)
        instance.information_source = information_source
      if instance.marking_structures:
        return instance

  def assemble_marking_structure(self, parent, json, cache_object):
    # TODO: detect polymorphism!
    instance = MarkingStructure()
    self.set_base(instance, json, cache_object, parent)
    if json:
      instance.id_ = json.get('id_', None)
      instance.marking_model_name = json.get('marking_model_name', None)
      instance.marking_model_ref = json.get('marking_model_ref', None)
      return instance

  def assemble_toolinformation(self, parent, json, cache_object):
    instance = ToolInformation()
    self.set_base(instance, json, cache_object, parent)
    if json:
      instance.id_ = json.get('id_', None)
      instance.idref = json.get('idref', None)
      if not instance.idref:
        instance.name = json.get('name', None)
        description = json.get('description', None)
        if description:
          description = self.assemble_structured_text(instance, description, cache_object)
          instance.description = description
        instance.vendor = json.get('vendor', None)
        instance.version = json.get('version', None)
        instance.service_pack = json.get('service_pack', None)
        instance.title = json.get('title', None)
        short_description = json.get('description', None)
        if short_description:
          short_description = self.assemble_structured_text(instance, short_description, cache_object)
          instance.short_description = short_description

      return instance

  def assemble_information_source_role(self, parent, json, cache_object):
    instance = InformationSourceRole()
    self.set_base(instance, json, cache_object, parent)
    if json:
      role = json.get('name', None)
      if role:
        instance.role = role
        return instance
