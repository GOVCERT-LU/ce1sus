# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""
from ce1sus.controllers.common.basechanger import BaseChanger
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.core.stix_header import STIXHeader, PackageIntent
from ce1sus.db.classes.cstix.indicator.indicator import Indicator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StixUpdater(BaseChanger):

  def assemble_stix_header(self, json, user, seen_groups=None, rest_insert=True, owner=False):
    instance = STIXHeader()
    self.set_base(instance, json, user, True, seen_groups, rest_insert, owner)
    if json:
      package_intents = json.get('package_intents', list())
      for package_intent in package_intents:
        package_intent = self.assemble_package_intent(package_intent, user, seen_groups, rest_insert, owner)
        instance.package_intents.append(package_intent)
      instance.title = json.get('title', None)
      description = json.get('description', None)
      if description:
        description = self.assemble_structured_text(description, user, True, seen_groups, rest_insert, owner)
        instance.description = description
      short_description = json.get('short_description', None)
      if short_description:
        short_description = self.assemble_structured_text(short_description, user, True, seen_groups, rest_insert, owner)
        instance.short_description = short_description
      handling = json.get('handling', None)
      if handling:
        handling = self.assemble_handling(handling, user, True, seen_groups, rest_insert, owner)
        instance.handling = handling
      information_source = json.get('information_source', None)
      if information_source:
        information_source = self.assemble_information_source(information_source, user, True, seen_groups, rest_insert, owner)
        instance.information_source = information_source
      return instance

  def assemble_package_intent(self, json, user, seen_groups=None, rest_insert=True, owner=False):
    instance = PackageIntent()
    self.set_base(instance, json, user, True, seen_groups, rest_insert, owner)
    if json:
      intent = json.get('intent', None)
      if intent:
        instance.intent = intent

  def assemble_indicator(self, event, json, user, owner=False, rest_insert=True, seen_groups=None, seen_attr_defs=None, seen_obj_defs=None):
    if seen_obj_defs is None:
      seen_obj_defs = dict()
    if seen_attr_defs is None:
      seen_attr_defs = dict()
    if seen_groups is None:
      seen_groups = dict()
    indicator = Indicator()
    indicator.uuid = json.get('identifier', None)
    indicator.event_id = event.identifier
    indicator.event = event
    indicator.populate(json, rest_insert)
    self.populate_extended_logging(indicator, json, user, True, seen_groups)
    description = json.get('description', None)
    if description:
      description = StructuredText(description)
      self.populate_extended_logging(description, json, user, True, seen_groups)
      indicator.description = description
    description = json.get('short_description', None)
    if description:
      description = StructuredText(description)
      self.populate_extended_logging(description, json, user, True, seen_groups)
      indicator.short_description = description
