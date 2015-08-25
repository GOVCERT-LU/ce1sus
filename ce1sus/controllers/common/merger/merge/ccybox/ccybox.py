# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 12, 2015
"""

from ce1sus.controllers.common.merger.base import BaseMerger
from ce1sus.controllers.common.merger.merge.ccybox.pseudo import PseudoCyboxMerger


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CyboxMerger(BaseMerger):

  def __init__(self, config, session=None):
    super(CyboxMerger, self).__init__(config, session)
    self.pseudo_cybox_merger = PseudoCyboxMerger(config, session)

  def merge_object(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.pseudo_cybox_merger.merge_object(old_instance, new_instance, merge_cache, attr_name)

  def merge_observables(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_observable, attr_name)

  def merge_observable(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'id_', merge_cache)
        self.update_instance_value(old_value, new_value, 'title', merge_cache)
        self.update_instance_value(old_value, new_value, 'idref', merge_cache)
        self.update_instance_value(old_value, new_value, 'sighting_count', merge_cache)

      elif merge_cache.result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)

      self.merge_keywords(old_value, new_value, merge_cache, 'keywords')
      self.merge_structured_text(old_value, new_value, merge_cache, 'description')

      self.pseudo_cybox_merger.merge_object(old_value, new_value, merge_cache, 'object')
      self.merge_observable_composition(old_value, new_value, merge_cache, 'observable_composition')

      self.set_base(old_value, new_value, merge_cache)
    return merge_cache.version

  def merge_observable_composition(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'operator', merge_cache)

      elif merge_cache.result == 0:
        self.set_value(old_value, new_value, attr_name, merge_cache)

      self.merge_observables(old_value, new_value, merge_cache, 'observables')

      self.set_base(old_value, new_value, merge_cache)
    return merge_cache.version

  def merge_keywords(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_keyword, attr_name)

  def merge_keyword(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'keyword', merge_cache)

      elif merge_cache.result == 0:
        self.set_value(old_value, new_value, attr_name, merge_cache)

      self.set_base(old_value, new_value, merge_cache)
    return merge_cache.version
