# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 12, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class STIXMerger(BaseMerger):

  def merge_stix_header(self, old_instance, new_instance, merge_cache):


    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'title', merge_cache))

      elif merge_cache.result == 0:
        old_instance = new_instance

      merge_cache.version.add(self.merge_structured_text(old_instance, new_instance, 'description', merge_cache))
      merge_cache.version.add(self.merge_structured_text(old_instance, new_instance, 'short_description', merge_cache))
      merge_cache.version.add(self.merge_package_intents(old_instance.package_intents, new_instance.package_intents, merge_cache))
      merge_cache.version.add(self.merge_handling(old_instance.handling, new_instance.handling, merge_cache))
      merge_cache.version.add(self.merge_information_source(old_instance.information_source, new_instance.information_source, merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version
