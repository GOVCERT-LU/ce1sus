# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from datetime import datetime

from ce1sus.db.classes.internal.usrmgt.group import EventPermissions
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CacheObject(object):

  def __init__(self, user=None, rest_insert=True, owner=False, insert=False, event_permissions=None, details=False, inflated=False, flat=None):
    self.event_permissions = event_permissions
    self.flat = flat
    self.details = details
    self.inflated = inflated
    self.insert = insert
    self.owner = owner
    self.user = user
    self.rest_insert = True
    self.seen_groups = dict()
    self.seen_attr_defs = dict()
    self.seen_obj_defs = dict()
    self.seen_ref_defs = dict()
    self.seen_conditions = dict()
    self.__created_at = None
    self.__modified_on = None
    self.modified_set = False

  @property
  def created_at(self):
    if self.__created_at is None:
      self.__created_at = datetime.utcnow()
    return self.__created_at

  @property
  def modified_on(self):
    if self.__modified_on is None:
      self.__modified_on = datetime.utcnow()
    return self.__modified_on

  @modified_on.setter
  def modified_on(self, value):
    self.__modified_on = value
    self.modified_set = True

  @property
  def complete(self):
    return self.details

  @complete.setter
  def complete(self, value):
    self.details = value

  def make_copy(self):
    cache_object = CacheObject()
    cache_object.event_permissions = self.event_permissions
    cache_object.flat = self.flat
    cache_object.details = self.details
    cache_object.inflated = self.inflated
    cache_object.insert = self.insert
    cache_object.owner = self.owner
    cache_object.user = self.user
    cache_object.rest_insert = self.rest_insert
    cache_object.seen_groups = self.seen_groups
    return cache_object

  def set_default(self):
    self.owner = True
    self.inflated = True
    self.complete = True
    self.event_permissions = EventPermissions('0')
    self.event_permissions.set_all()


  def reset(self):
    self.__created_at = None
    self.__modified_on = None

class MergerCache(CacheObject):

  def __init__(self, cache_object):
    super(MergerCache, self).__init__(cache_object.user, cache_object.rest_insert, cache_object.owner, cache_object.insert, cache_object.event_permissions, cache_object.details, cache_object.inflated, cache_object.flat)
    # result: -1: Do nothing 0: Add items (major update) 1: merge version inside 2:minor update
    self.result = -1
    self.version = Version()
    self.__inc_lvl = 0
    self.changed_versions = dict()

  def make_copy(self):
    cache_object = super(MergerCache, self).make_copy()
    merger_cache = MergerCache(cache_object)
    merger_cache.result = self.result
    merger_cache.version = self.version
    merger_cache.changed_versions = self.changed_versions
    return merger_cache

  def inc_version_major(self):
    if self.__inc_lvl < 3:
      self.__inc_lvl = 3
      self.version.increase_major()

  def inc_version_minior(self):
    if self.__inc_lvl < 2:
      self.__inc_lvl = 2
      self.version.increase_minor()

  def inc_version_patch(self):
    if self.__inc_lvl < 1:
      self.__inc_lvl = 1
      self.version.increase_patch()
      
  def __inst_id(self, instance):
    return '{0}{1}'.format(instance.get_classname(),instance.uuid)
    
  def is_changed_version(self, instance):
    id_ = self.__inst_id(instance)
    return self.changed_versions.get(id_, False)

  def set_changed_version(self, instance):
    id_ = self.__inst_id(instance)
    self.changed_versions[id_] = True
    
  def reset(self):
    super(MergerCache, self).reset()
    self.result = -1
    self.version = Version()
    self.__inc_lvl = 0
    self.changed_versions = dict()
