# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import DateTime

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.common.relations import _REL_STARTTIME_DATETIMEWITHPRECISION, _REL_ENDTIME_DATETIMEWITHPRECISION, \
  _REL_PRODUCEDTIME_DATETIMEWITHPRECISION, _REL_RECEIVEDTIME_DATETIMEWITHPRECISION
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.relations import _REL_ACTIVITY_STRUCTUREDTEXT, _REL_ACTIVITY_DATETIMEWITHPRECISION
from ce1sus.db.classes.cstix.exploit_target.relations import _REL_VULNERABILITY_PUB_DATETIMEWITHPRECISION, _REL_VULNERABILITY_DIS_DATETIMEWITHPRECISION
from ce1sus.db.classes.cstix.incident.relations import _REL_COATIME_DATETIME_START, _REL_COATIME_DATETIME_ENDED, _REL_FMA_DATETIMEWITHPRECISION, \
  _REL_IC_DATETIMEWITHPRECISION, _REL_FAE_DATETIMEWITHPRECISION, _REL_IO_DATETIMEWITHPRECISION, _REL_CA_DATETIMEWITHPRECISION, _REL_RA_DATETIMEWITHPRECISION, \
  _REL_IR_DATETIMEWITHPRECISION, _REL_ICL_DATETIMEWITHPRECISION
from ce1sus.db.classes.internal.corebase import UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class DateTimeWithPrecision(Entity, Base):

  value = Column('value', DateTime)
  precision = Column('precision', UnicodeType(10))
  
  cyboxtime_start = relationship('CyboxTime', secondary=_REL_STARTTIME_DATETIMEWITHPRECISION, uselist=False)
  cyboxtime_end = relationship('CyboxTime', secondary=_REL_ENDTIME_DATETIMEWITHPRECISION, uselist=False)
  cyboxtime_produced = relationship('CyboxTime', secondary=_REL_PRODUCEDTIME_DATETIMEWITHPRECISION, uselist=False)
  cyboxtime_received = relationship('CyboxTime', secondary=_REL_RECEIVEDTIME_DATETIMEWITHPRECISION, uselist=False)
  activity = relationship('Activity', secondary=_REL_ACTIVITY_DATETIMEWITHPRECISION, uselist=False)
  vulnerability_publish = relationship('Vulnerability', secondary=_REL_VULNERABILITY_PUB_DATETIMEWITHPRECISION, uselist=False)
  vulnerability_discovered = relationship('Vulnerability', secondary=_REL_VULNERABILITY_DIS_DATETIMEWITHPRECISION, uselist=False)
  coa_time_start = relationship('COATime', uselist=False, secondary=_REL_COATIME_DATETIME_START)
  coa_time_end = relationship('COATime', uselist=False, secondary=_REL_COATIME_DATETIME_ENDED)
  time_fma = relationship('Time', secondary=_REL_FMA_DATETIMEWITHPRECISION, uselist=False)
  time_ic = relationship('Time', secondary=_REL_IC_DATETIMEWITHPRECISION, uselist=False)
  time_fae = relationship('Time', secondary=_REL_FAE_DATETIMEWITHPRECISION, uselist=False)
  time_io = relationship('Time', secondary=_REL_IO_DATETIMEWITHPRECISION, uselist=False)
  time_ca = relationship('Time', secondary=_REL_CA_DATETIMEWITHPRECISION, uselist=False)
  time_ra = relationship('Time', secondary=_REL_RA_DATETIMEWITHPRECISION, uselist=False)
  time_ir = relationship('Time', secondary=_REL_IR_DATETIMEWITHPRECISION, uselist=False)
  time_icl = relationship('Time', secondary=_REL_ICL_DATETIMEWITHPRECISION, uselist=False)

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
