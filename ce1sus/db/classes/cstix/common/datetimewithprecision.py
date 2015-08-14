# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.core import UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class DateTimeWithPrecision(Entity, Base):

  value = Column('value', DateTime)
  precision = Column('precision', UnicodeType(10))
  
  @property
  def parent(self):
    if self.cyboxtime_start:
      return self.cyboxtime_start
    elif self.cyboxtime_end:
      return self.cyboxtime_end
    elif self.cyboxtime_produced:
      return self.cyboxtime_produced
    elif self.cyboxtime_received:
      return self.cyboxtime_received
    elif self.vulnerability_publish:
      return self.vulnerability_publish
    elif self.vulnerability_discovered:
      return self.vulnerability_discovered
    elif self.activity:
      return self.activity
    elif self.time_fma:
      return self.time_fma
    elif self.time_ic:
      return self.time_ic
    elif self.time_fae:
      return self.time_fae
    elif self.time_io:
      return self.time_io
    elif self.time_ca:
      return self.time_ca
    elif self.time_ra:
      return self.time_ra
    elif self.time_ir:
      return self.time_ir
    elif self.time_icl:
      return self.time_icl
    elif self.coa_time_start:
      return self.coa_time_start
    elif self.coa_time_end:
      return self.coa_time_end
    raise ValueError('Parent not found')

  def to_dict(self, cache_object):

    result = {
              'value': self.convert_value(self.value),
              'precision': self.convert_value(self.precision),
            }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
