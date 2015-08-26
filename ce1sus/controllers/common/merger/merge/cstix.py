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

  def merge_stix_header(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:

      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'title', merge_cache)
        self.set_base(old_value, new_value, merge_cache)

      elif merge_cache.result == 0:
        old_instance = new_instance

      self.merge_structured_text(old_value, new_value, merge_cache, 'description')
      self.merge_structured_text(old_value, new_value, merge_cache, 'short_description')
      self.merge_package_intents(old_value, new_value, merge_cache, 'package_intents')
      self.merge_handling(old_value, new_value, merge_cache, 'handling')
      self.merge_information_source(old_value, new_value, merge_cache, 'information_source')


    return merge_cache.version
