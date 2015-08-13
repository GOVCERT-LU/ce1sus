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


class StixAssembler(BaseChanger):

  def __init__(self, config, session=None):
    super(StixAssembler, self).__init__(config, session)

  def assemble_stix_header(self, event, json, cache_object):
    instance = STIXHeader()
    self.set_base(instance, json, cache_object, event)
    if json:
      package_intents = json.get('package_intents', list())
      for package_intent in package_intents:
        package_intent = self.assemble_package_intent(event, package_intent, cache_object)
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

  def assemble_package_intent(self, event, json, cache_object):
    instance = PackageIntent()
    self.set_base(instance, json, cache_object, event)
    if json:
      intent = json.get('intent', None)
      if intent:
        instance.intent = intent

  def assemble_indicator(self, event, json, cache_object):
    raise
