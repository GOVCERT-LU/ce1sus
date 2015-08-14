# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 12, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class STIXMerger(BaseMerger):

  def merge_stix_header(self, old_instance, new_instance, cache_object):

    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'title', cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    version.add(self.merge_structured_text(old_instance.description, new_instance.description, cache_object))
    version.add(self.merge_structured_text(old_instance.short_description, new_instance.short_description, cache_object))
    version.add(self.merge_package_intents(old_instance.package_intents, new_instance.package_intents, cache_object))
    version.add(self.merge_handling(old_instance.handling, new_instance.handling, cache_object))
    version.add(self.merge_information_source(old_instance.information_source, new_instance.information_source, cache_object))

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version
