# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 28, 2015
"""

from types import NoneType

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.core import BaseElement


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Entity(BaseElement):

  def parse_id(self, id_):
    if id_:
      i = id_.index(':')
      if i > 0:
        namespace = id_[0:i]
        i = id_.index('-')
        if i > 0:
          uuid = id_[i + 1:]
          return namespace, uuid
        else:
          return namespace, None
    return 'ce1sus', None

  _PARENTS = list()

  @property
  def parent(self):
    for attr_name in self._PARENTS:
      if hasattr(self, attr_name):
        item = getattr(self, attr_name)
        if item:
          return item
    raise ValueError('Parent cannot be found')

  @parent.setter
  def parent(self, instance):
    # TODO: verify if this is feasible for long term (note as there can be more parents)
    parent_set = False
    if len(self._PARENTS) == 1:
      attr_name = self._PARENTS[0]
      if hasattr(self, attr_name):
        setattr(self, attr_name, instance)
        parent_set = True
      if not parent_set:
        if self.get_classname() != 'Event':
          raise ValueError('Cannot find parent')
    else:
      raise ValueError('There are too many or no possible parent(s)')

  def delink_parent(self):
    for attr_name in self._PARENTS:
      if hasattr(self, attr_name):
        item = getattr(self, attr_name)
        if isinstance(item, Entity) or isinstance(item, NoneType):
          setattr(self, attr_name, None)
        else:
          setattr(self, attr_name, list())

  @property
  def root(self):
    parent = self.parent
    if parent:
      if parent.get_classname() == 'Event':
        return parent
      else:
        return parent.root
    else:
      return self

  def set_id(self, id_):
    namespace, uuid = self.parse_id(id_)
    if namespace and not self.namespace:
      self.namespace = namespace
    if uuid and not self.uuid:
      self.uuid = uuid

  def to_dict(self, cache_object):
    result = {}
    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)