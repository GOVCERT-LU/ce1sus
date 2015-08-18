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

class PseudoCyboxMerger(BaseMerger):

  def merge_object(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'id_', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'idref', merge_cache))

      elif merge_cache.result == 0:
        merge_cache.version.add(merge_cache.version().increase_major()())
        merge_cache.object_changes = True
        old_instance = new_instance

      merge_cache.version.add(self.merge_attributes(old_instance.attributes, new_instance.attributes, merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_attributes(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_attribute)

  def merge_attribute(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'value', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'is_ioc', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'condition_id', merge_cache))

      elif merge_cache.result == 0:
        merge_cache.version.add(merge_cache.version().increase_major()())
        merge_cache.object_changes = True
        old_instance = new_instance

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version
