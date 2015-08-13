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

class PseudoCyboxMerger(BaseMerger):

  def merge_object(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'id_', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'idref', cache_object))
      version.add(self.merge_attributes(old_instance.attribtues, new_instance.attribtues, cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_attributes(self, new_instance, old_instance, cache_object):
    return self.merge_gen_arrays(new_instance, old_instance, cache_object, self.merge_attribute)

  def merge_attribute(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'value', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'is_ioc', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'condition_id', cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version
