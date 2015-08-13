# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 28, 2015
"""

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
