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

  def merge_object(self, old_instance, new_instance, merge_cache):
    return self.pseudo_cybox_merger.merge_object(old_instance, new_instance, merge_cache)

  def merge_observables(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_observable)

  def merge_observable(self, old_instance, new_instance, merge_cache):
    
    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'id_', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'title', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'idref', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'sighting_count', merge_cache))

      elif merge_cache.result == 0:
        merge_cache.version.add(merge_cache.version().increase_major()())
        old_instance = new_instance

      merge_cache.version.add(self.merge_keywords(old_instance.keywords, new_instance.keywords, merge_cache))
      merge_cache.version.add(self.merge_structured_text(old_instance.description, new_instance.description, merge_cache))

      merge_cache.version.add(self.pseudo_cybox_merger.merge_object(old_instance.object, new_instance.object, merge_cache))
      merge_cache.version.add(self.merge_observable_composition(old_instance.observable_composition, new_instance.observable_composition, merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_observable_composition(self, old_instance, new_instance, merge_cache):
    
    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'operator', merge_cache))

      elif merge_cache.result == 0:
        merge_cache.version.add(merge_cache.version().increase_major()())
        old_instance = new_instance

      merge_cache.version.add(self.merge_observables(old_instance.observables, new_instance.observables, merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_keywords(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_keyword)

  def merge_keyword(self, old_instance, new_instance, merge_cache):
    
    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'keyword', merge_cache))

      elif merge_cache.result == 0:
        merge_cache.version.add(merge_cache.version().increase_major()())
        old_instance = new_instance

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version
