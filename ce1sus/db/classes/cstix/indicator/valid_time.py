# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class ValidTime(Entity, Base):

  # due to backwards comparability
  __tablename__ = 'validtimepositions'
  identifier = Column(u'validtimeposition_id', BigIntegerType, primary_key=True, autoincrement=True, nullable=False, index=True, unique=True)

  start_time = Column('start_time', DateTime, nullable=False)
  end_time = Column('end_time', DateTime, nullable=False)
  indicator_id = Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  _PARENTS = ['indicator']
  indicator = relationship('Indicator', uselist=False)

  def to_dict(self, cache_object):

    result = {
              'start_time': self.convert_value(self.start_time),
              'end_time': self.convert_value(self.end_time),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
