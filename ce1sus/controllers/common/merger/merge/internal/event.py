# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger
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


  def merge_event(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'idref', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'status_id', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'risk_id', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'analysis_id', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'last_seen', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'first_seen', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'last_publish_date', merge_cache))

      elif merge_cache.result == 0:
        old_instance = new_instance
        merge_cache.object_changes = True
      # check if sub elements were changed
      merge_cache.version.add(self.cybox_merger.merge_observables(old_instance.observables, new_instance.observables, merge_cache))
      merge_cache.version.add(self.merge_reports(old_instance.reports, new_instance.reports, merge_cache))
      merge_cache.version.add(self.stix_merger.merge_stix_header(old_instance.stix_header, new_instance.stix_header, merge_cache))

      self.set_version(old_instance, new_instance, merge_cache)
      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_reports(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_report)

  def merge_report(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'title', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'description', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'short_description', merge_cache))
        # TODO: related reports
        merge_cache.version.add(self.merge_references(old_instance.references, new_instance.references, merge_cache))

      elif merge_cache.result == 0:
        old_instance = new_instance
        merge_cache.object_changes = True

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_references(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_reference)

  def merge_reference(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      merge_cache.result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if merge_cache.result == 1:
        # Definition cannot be changed
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'value', merge_cache))
        # TODO: reference children

      elif merge_cache.result == 0:
        old_instance = new_instance
        merge_cache.object_changes = True

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version
