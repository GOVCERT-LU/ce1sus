# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.incident.relations import _REL_FMA_DATETIMEWITHPRECISION, _REL_IC_DATETIMEWITHPRECISION, _REL_FAE_DATETIMEWITHPRECISION, \
  _REL_IO_DATETIMEWITHPRECISION, _REL_CA_DATETIMEWITHPRECISION, _REL_RA_DATETIMEWITHPRECISION, _REL_IR_DATETIMEWITHPRECISION, _REL_ICL_DATETIMEWITHPRECISION
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Time(Entity, Base):

  __tablename__ = 'stixtimes'

  first_malicious_action = relationship(DateTimeWithPrecision, secondary=_REL_FMA_DATETIMEWITHPRECISION, uselist=False)
  initial_compromise = relationship(DateTimeWithPrecision, secondary=_REL_IC_DATETIMEWITHPRECISION, uselist=False)
  first_data_exfiltration = relationship(DateTimeWithPrecision, secondary=_REL_FAE_DATETIMEWITHPRECISION, uselist=False)
  incident_opened = relationship(DateTimeWithPrecision, secondary=_REL_IO_DATETIMEWITHPRECISION, uselist=False)
  containment_achieved = relationship(DateTimeWithPrecision, secondary=_REL_CA_DATETIMEWITHPRECISION, uselist=False)
  restoration_achieved = relationship(DateTimeWithPrecision, secondary=_REL_RA_DATETIMEWITHPRECISION, uselist=False)
  incident_reported = relationship(DateTimeWithPrecision, secondary=_REL_IR_DATETIMEWITHPRECISION, uselist=False)
  incident_closed = relationship(DateTimeWithPrecision, secondary=_REL_ICL_DATETIMEWITHPRECISION, uselist=False)

  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  incident = relationship('Incident', uselist=False)
  _PARENTS = ['incident']

  def to_dict(self, cache_object):

    result = {
              'first_malicious_action': self.attribute_to_dict(self.first_malicious_action, cache_object),
              'initial_compromise': self.attribute_to_dict(self.initial_compromise, cache_object),
              'first_data_exfiltration': self.attribute_to_dict(self.first_data_exfiltration, cache_object),
              'incident_opened': self.attribute_to_dict(self.incident_opened, cache_object),
              'containment_achieved': self.attribute_to_dict(self.containment_achieved, cache_object),
              'restoration_achieved': self.attribute_to_dict(self.restoration_achieved, cache_object),
              'incident_reported': self.attribute_to_dict(self.incident_reported, cache_object),
              'incident_closed': self.attribute_to_dict(self.incident_closed, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
