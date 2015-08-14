# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from copy import deepcopy
from datetime import datetime


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

  @property
  def complete(self):
    return self.details

  @complete.setter
  def complete(self, value):
    self.details = value

  def make_copy(self):
    return deepcopy(self)


