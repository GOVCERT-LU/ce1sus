# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.common.relations import _REL_STARTTIME_DATETIMEWITHPRECISION, _REL_ENDTIME_DATETIMEWITHPRECISION, \
  _REL_PRODUCEDTIME_DATETIMEWITHPRECISION, _REL_RECEIVEDTIME_DATETIMEWITHPRECISION
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class CyboxTime(Entity, Base):

  start_time = relationship(DateTimeWithPrecision, secondary=_REL_STARTTIME_DATETIMEWITHPRECISION, uselist=False, back_populates='cyboxtime_start')
  end_time = relationship(DateTimeWithPrecision, secondary=_REL_ENDTIME_DATETIMEWITHPRECISION, uselist=False, back_populates='cyboxtime_end')
  produced_time = relationship(DateTimeWithPrecision, secondary=_REL_PRODUCEDTIME_DATETIMEWITHPRECISION, uselist=False, back_populates='cyboxtime_produced')
  received_time = relationship(DateTimeWithPrecision, secondary=_REL_RECEIVEDTIME_DATETIMEWITHPRECISION, uselist=False, back_populates='cyboxtime_received')

  _PARENTS = ['information_source']

  informationsource_id = Column(BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  information_source = relationship('InformationSource', uselist=False)

  def to_dict(self, cache_object):
    instance = self.get_populated(cache_object)

    result = {'start_time': instance.attribute_to_dict(instance.start_time, cache_object),
              'end_time':instance.attribute_to_dict(instance.end_time, cache_object),
              'produced_time':instance.attribute_to_dict(instance.produced_time, cache_object),
              'received_time':instance.attribute_to_dict(instance.received_time, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
