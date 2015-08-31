# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger, MergerException
from ce1sus.controllers.common.merger.merge.ccybox.ccybox import CyboxMerger
from ce1sus.controllers.common.merger.merge.cstix import STIXMerger


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventMerger(BaseMerger):

  def __init__(self, config, session=None):
    super(EventMerger, self).__init__(config, session)
    self.cybox_merger = CyboxMerger(config, session)
    self.stix_merger = STIXMerger(config, session)

  def merge_event_group_permission(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'dbcode', merge_cache)
        self.update_instance_value(old_value, new_value, 'dbcode', merge_cache)
      elif merge_cache.result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)

      self.set_base(old_value, new_instance, merge_cache)
    return merge_cache.version

  def merge_event(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'idref', merge_cache)
        self.update_instance_value(old_value, new_value, 'status_id', merge_cache)
        self.update_instance_value(old_value, new_value, 'risk_id', merge_cache)
        self.update_instance_value(old_value, new_value, 'analysis_id', merge_cache)
        self.update_instance_value(old_value, new_value, 'last_seen', merge_cache)
        self.update_instance_value(old_value, new_value, 'first_seen', merge_cache)
        self.update_instance_value(old_value, new_value, 'last_publish_date', merge_cache)

        self.set_version(old_value, new_value, merge_cache)
        self.set_base(old_value, new_value, merge_cache)

      elif merge_cache.result == 0:
        raise MergerException('The event wanted to be merge does not exist')
      # check if sub elements were changed
      self.cybox_merger.merge_observables(old_value, new_value, merge_cache, 'observables')
      self.merge_reports(old_value, new_value, merge_cache, 'reports')
      self.stix_merger.merge_stix_header(old_value, new_value, merge_cache, 'stix_header')



    return merge_cache.version

  def merge_reports(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_report, attr_name)

  def merge_report(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_instance:
      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'title', merge_cache)
        # TODO: related reports
        
      elif merge_cache.result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)
        
      self.merge_references(old_value, new_value, merge_cache, 'references')

      self.merge_structured_text(old_value, new_value, merge_cache, 'description')
      self.merge_structured_text(old_value, new_value, merge_cache, 'short_description')


      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_references(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_reference, attr_name)

  def merge_reference(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      if len(old_value) > 1:
        raise MergerException('Multiple reference mergeing is not supported')

      merge_cache.result = self.is_mergeable(old_value, new_value[0], merge_cache)
      if merge_cache.result == 1:
        # Definition cannot be changed
        self.update_instance_value(old_value, new_value[0], 'value', merge_cache)

      self.set_base(old_value, new_value[0], merge_cache)
    return merge_cache.version
