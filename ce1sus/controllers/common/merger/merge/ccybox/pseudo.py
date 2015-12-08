# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 12, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger, MergerException
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class PseudoCyboxMerger(BaseMerger):

  def __init__(self, config, session=None):
    super(PseudoCyboxMerger, self).__init__(config, session)
    self.condition_broker = self.broker_factory(ConditionBroker)

  def get_condition(self, uuid, cache_object):
    definition = cache_object.seen_conditions.get(uuid, None)
    if definition:
      return definition
    else:
      # TODO: catch exceptions
      definition = self.condition_broker.get_by_uuid(uuid)
      cache_object.seen_conditions[uuid] = definition
      return definition

  def merge_object(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      merge_cache.result = self.is_mergeable(old_value, new_instance, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'id_', merge_cache)
        self.update_instance_value(old_value, new_value, 'idref', merge_cache)
        self.set_base(old_value, new_value, merge_cache)

      elif merge_cache.result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)

      self.merge_attributes(old_value, new_value, merge_cache, 'attributes')

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
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    old_value = self.__get_attr_value(old_value)
    new_value = self.__get_attr_value(new_value)
    if old_value or new_value:

      merge_cache.result = self.is_mergeable(old_value, new_value, merge_cache)
      if merge_cache.result == 1:
        self.update_instance_value(old_value, new_value, 'value', merge_cache)
        self.update_instance_value(old_value, new_value, 'is_ioc', merge_cache)
        
        self.set_base(old_value, new_value, merge_cache)

      elif merge_cache.result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)
      
      self.merge_confidence(old_instance, new_instance, merge_cache, 'condition')
      

    return merge_cache.version
  
  def merge_confidence(self, old_instance, new_instance, merge_cache, attr_name=None):
    new_value = self.get_values(old_instance, new_instance, attr_name)[1]
    if new_value:
      old_instance.condition = self.get_condition(new_value.uuid, merge_cache)
    else:
      old_instance.condition = None
    return merge_cache.version


