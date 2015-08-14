# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.coa.coa import CourseOfAction
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.common.vocabs import HighMediumLow
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_COATAKEN_COA = Table('rel_coataken_courseofaction', getattr(Base, 'metadata'),
                          Column('rctc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                          Column('coataken_id',
                                 BigIntegerType,
                                 ForeignKey('coatakens.coataken_id',
                                            ondelete='cascade',
                                            onupdate='cascade'),
                                 index=True,
                                 nullable=False),
                          Column('structuredtext_id',
                                 BigIntegerType,
                                 ForeignKey('courseofactions.courseofaction_id',
                                            ondelete='cascade',
                                            onupdate='cascade'),
                                 nullable=False,
                                 index=True)
                          )

_REL_COAREQUESTED_COA = Table('rel_coarequested_courseofaction', getattr(Base, 'metadata'),
                          Column('rcrc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                          Column('coarequested_id',
                                 BigIntegerType,
                                 ForeignKey('coarequesteds.coarequested_id',
                                            ondelete='cascade',
                                            onupdate='cascade'),
                                 index=True,
                                 nullable=False),
                          Column('structuredtext_id',
                                 BigIntegerType,
                                 ForeignKey('courseofactions.courseofaction_id',
                                            ondelete='cascade',
                                            onupdate='cascade'),
                                 nullable=False,
                                 index=True)
                          )

_REL_COATIME_DATETIME_START = Table('rel_coatime_datetime_start', getattr(Base, 'metadata'),
                                    Column('rcsd_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('coatime_id',
                                           BigIntegerType,
                                           ForeignKey('coatimes.coatime_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('datetimewithprecision_id',
                                           BigIntegerType,
                                           ForeignKey('datetimewithprecisions.datetimewithprecision_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           index=True)
                                    )

_REL_COATIME_DATETIME_ENDED = Table('rel_coatime_datetime_end', getattr(Base, 'metadata'),
                                    Column('rced_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('coatime_id',
                                           BigIntegerType,
                                           ForeignKey('coatimes.coatime_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('datetimewithprecision_id',
                                           BigIntegerType,
                                           ForeignKey('datetimewithprecisions.datetimewithprecision_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           index=True)
                                    )

_REL_COATAKEN_COATIME = Table('rel_coataken_coatime', getattr(Base, 'metadata'),
                                    Column('rctct_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('coataken_id',
                                           BigIntegerType,
                                           ForeignKey('coatakens.coataken_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('coatime_id',
                                           BigIntegerType,
                                           ForeignKey('coatimes.coatime_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           index=True)
                                    )

_REL_COAREQUESTED_COATIME = Table('rel_coarequested_coatime', getattr(Base, 'metadata'),
                                    Column('rctct_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('coarequested_id',
                                           BigIntegerType,
                                           ForeignKey('coarequesteds.coarequested_id',
                                                      ondelete='cascade',
                                                      onupdate='cascade'),
                                           index=True,
                                           nullable=False),
                                    Column('coatime_id',
                                           BigIntegerType,
                                           ForeignKey('coatimes.coatime_id',
                                                      ondelete='cascade',
                                                onupdate='cascade'),
                                           nullable=False,
                                           index=True)
                                    )


class COATime(Entity, Base):
  start = relationship(DateTimeWithPrecision, secondary=_REL_COATIME_DATETIME_START, uselist=False, backref='coa_time_start')
  end = relationship(DateTimeWithPrecision, secondary=_REL_COATIME_DATETIME_ENDED, uselist=False, backref='coa_time_end')

  _PARENTS = ['coa_taken', 'coa_requested']

  def to_dict(self, cache_object):

    result = {
              'start': self.attribute_to_dict(self.start, cache_object),
              'end': self.attribute_to_dict(self.end, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class COATaken(Entity, Base):
  time = relationship(COATime, secondary=_REL_COATAKEN_COATIME, backref='coa_taken')
  course_of_action = relationship(CourseOfAction, secondary=_REL_COATAKEN_COA, backref='coa_taken')
  # TODO: Contributors
  # contributors = Contributors()

  _PARENTS = ['incident', 'history_item']

  def to_dict(self, cache_object):

    result = {
              'time': self.attribute_to_dict(self.time, cache_object),
              'course_of_action': self.attribute_to_dict(self.course_of_action, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class COARequested(Entity, Base):
  time = relationship(COATime, secondary=_REL_COAREQUESTED_COATIME, backref='coa_requested')
  course_of_action = relationship(CourseOfAction, secondary=_REL_COAREQUESTED_COA, backref='coa_requested')

  # TODO: Contributors
  # contributors = Contributors()
  priority_id = Column('priority_id', Integer)
  __priority = None

  @property
  def priority(self):
    if not self.__priority:
      if self.priority_id:
        self.__priority = HighMediumLow(self, 'priority_id')
      else:
        return None
    return self.__priority.name

  @priority.setter
  def priority(self, value):
    if not self.priority:
      self.__priority = HighMediumLow(self, 'priority_id')
    self.priority.name = value

  _PARENTS = ['incident']

  def to_dict(self, cache_object):

    result = {
              'time': self.attribute_to_dict(self.time, cache_object),
              'course_of_action': self.attribute_to_dict(self.course_of_action, cache_object),
              'priority': self.convert_value(self.priority)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
