# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 12, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger, MergerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class PseudoCyboxMerger(BaseMerger):

  def merge_object(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      merge_cache.result = self.is_mergeable(old_value, new_instance, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'id_', merge_cache)
        self.update_instance_value(old_value, new_value, 'idref', merge_cache)

      elif merge_cache.result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)

      self.merge_attributes(old_value, new_value, merge_cache, 'attributes')

      self.set_base(old_value, new_value, merge_cache)
    return merge_cache.version
  
  def merge_attributes(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_attribute, attr_name)

  def __get_attr_value(self, instance):
    if isinstance(instance, list):
      if len(instance) > 1:
        raise MergerException('Multiple attribute mergeing is not supported')
      return instance[0]
    return instance

  def merge_attribute(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(self.__get_attr_value(old_instance), self.__get_attr_value(new_instance), attr_name)
    if old_value or new_value:

      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'value', merge_cache)
        self.update_instance_value(old_value, new_value, 'is_ioc', merge_cache)
        self.update_instance_value(old_value, new_value, 'condition_id', merge_cache)

      elif merge_cache.result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)

      self.set_base(old_value, new_value, merge_cache)
    return merge_cache.version
