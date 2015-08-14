# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger
from ce1sus.controllers.common.merger.merge.ccybox.ccybox import CyboxMerger
from ce1sus.controllers.common.merger.merge.cstix import STIXMerger
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventMerger(BaseMerger):

  def __init__(self, config, session=None):
    super(EventMerger, self).__init__(config, session)
    self.cybox_merger = CyboxMerger(config, session)
    self.stix_merger = STIXMerger(config, session)


  def merge_event(self, old_instance, new_instance, cache_object):

    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'idref', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'status_id', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'risk_id', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'analysis_id', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'last_seen', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'first_seen', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'last_publish_date', cache_object))

      self.set_base(old_instance, new_instance, cache_object)

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    # check if sub elements were changed
    version.add(self.cybox_merger.merge_observables(old_instance.observables, new_instance.observables, cache_object))
    version.add(self.merge_reports(old_instance.reports, new_instance.reports, cache_object))

    version.add(self.stix_merger.merge_stix_header(old_instance.stix_header, new_instance.stix_header, cache_object))
    
    #If the newversion is newer take this one
    if old_instance.version.compare(new_instance.version) > 0:
      self.update_instance_value(old_instance.version, new_instance.version, 'version', cache_object)
    else:
      # set the new version
      old_instance.version.add(version)



    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_reports(self, old_instance, new_instance, cache_object):
    return self.merge_gen_arrays(old_instance, new_instance, cache_object, self.merge_report)

  def merge_report(self, old_instance, new_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'title', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'description', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'short_description', cache_object))
      # TODO: related reports
      version.add(self.merge_references(old_instance.references, new_instance.references, cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_references(self, old_instance, new_instance, cache_object):
    return self.merge_gen_arrays(old_instance, new_instance, cache_object, self.merge_reference)

  def merge_reference(self, old_instance, new_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      # Definition cannot be changed
      version.add(self.update_instance_value(old_instance, new_instance, 'value', cache_object))
      # TODO: reference children

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version
