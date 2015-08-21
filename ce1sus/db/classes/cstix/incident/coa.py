# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.coa.coa import CourseOfAction
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.common.vocabs import HighMediumLow
from ce1sus.db.classes.cstix.incident.relations import _REL_COATIME_DATETIME_START, _REL_COATIME_DATETIME_ENDED, _REL_COATAKEN_COATIME, _REL_COATAKEN_COA, \
  _REL_COAREQUESTED_COATIME, _REL_COAREQUESTED_COA, _REL_HISTORYITEM_COATAKEN, _REL_INCIDENT_COATAKEN, _REL_INCIDENT_COAREQUESTED
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class COATime(Entity, Base):
  start = relationship(DateTimeWithPrecision, secondary=_REL_COATIME_DATETIME_START, uselist=False)
  end = relationship(DateTimeWithPrecision, secondary=_REL_COATIME_DATETIME_ENDED, uselist=False)
  coa_taken = relationship('COATaken', uselist=False, secondary=_REL_COATAKEN_COATIME)
  _PARENTS = ['coa_taken', 'coa_requested']
  coa_requested = relationship('COARequested', uselist=False, secondary=_REL_COAREQUESTED_COATIME)


  def to_dict(self, cache_object):

    result = {
              'start': self.attribute_to_dict(self.start, cache_object),
              'end': self.attribute_to_dict(self.end, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class COATaken(Entity, Base):
  time = relationship(COATime, secondary=_REL_COATAKEN_COATIME)
  course_of_action = relationship(CourseOfAction, secondary=_REL_COATAKEN_COA)
  # TODO: Contributors
  # contributors = Contributors()

  _PARENTS = ['incident', 'history_item']
  history_item = relationship('HistoryItem', uselist=False, secondary=_REL_HISTORYITEM_COATAKEN)
  incident = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_COATAKEN)


  def to_dict(self, cache_object):

    result = {
              'time': self.attribute_to_dict(self.time, cache_object),
              'course_of_action': self.attribute_to_dict(self.course_of_action, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class COARequested(Entity, Base):
  time = relationship(COATime, secondary=_REL_COAREQUESTED_COATIME)
  course_of_action = relationship(CourseOfAction, secondary=_REL_COAREQUESTED_COA)

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
  incident = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_COAREQUESTED)
  def to_dict(self, cache_object):

    result = {
              'time': self.attribute_to_dict(self.time, cache_object),
              'course_of_action': self.attribute_to_dict(self.course_of_action, cache_object),
              'priority': self.convert_value(self.priority)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
