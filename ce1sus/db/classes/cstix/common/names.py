# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.schema import Column

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.corebase import UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Name(Entity, Base):

  name = Column('name', UnicodeType(255), default=None, nullable=False)
  # reference = anyuri
  reference = Column('reference', UnicodeType(255), default=None, nullable=False)

  _PARENTS = ['campaign']

  def to_dict(self, cache_object):
    result = {
              'name':self.convert_value(self.name),
              'reference':self.convert_value(self.reference),
             }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
