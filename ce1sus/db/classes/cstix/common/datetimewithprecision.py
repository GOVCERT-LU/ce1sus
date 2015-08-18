# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.corebase import UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class DateTimeWithPrecision(Entity, Base):

  value = Column('value', DateTime)
  precision = Column('precision', UnicodeType(10))
  
  _PARENTS = ['cyboxtime_start',
              'cyboxtime_end',
              'cyboxtime_produced',
              'cyboxtime_received',
              'vulnerability_publish',
              'vulnerability_discovered',
              'activity',
              'time_fma',
              'time_ic',
              'time_fae',
              'time_io',
              'time_ca',
              'time_ra',
              'time_ir',
              'time_icl',
              'coa_time_start',
              'coa_time_end']

  def to_dict(self, cache_object):

    result = {
              'value': self.convert_value(self.value),
              'precision': self.convert_value(self.precision),
            }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
