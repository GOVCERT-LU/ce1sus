# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_STARTTIME_DATETIMEWITHPRECISION = Table('rel_starttime_datetimewithprecision', getattr(Base, 'metadata'),
                                              Column('rstdwp_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
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

_REL_ENDTIME_DATETIMEWITHPRECISION = Table('rel_endtime_datetimewithprecision', getattr(Base, 'metadata'),
                                              Column('retdwp_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
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

_REL_PRODUCEDTIME_DATETIMEWITHPRECISION = Table('rel_producedtime_datetimewithprecision', getattr(Base, 'metadata'),
                                              Column('rptdwp_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
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

_REL_RECEIVEDTIME_DATETIMEWITHPRECISION = Table('rel_receivedtime_datetimewithprecision', getattr(Base, 'metadata'),
                                              Column('rrtdwp_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                              Column('cyboxtime_id',
                                                     BigIntegerType,
                                                     ForeignKey('cyboxtimes.cyboxtime_id',
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

class CyboxTime(Entity, Base):

  start_time = relationship(DateTimeWithPrecision, secondary=_REL_STARTTIME_DATETIMEWITHPRECISION, uselist=False, backref='cyboxtime_start')
  end_time = relationship(DateTimeWithPrecision, secondary=_REL_ENDTIME_DATETIMEWITHPRECISION, uselist=False, backref='cyboxtime_end')
  produced_time = relationship(DateTimeWithPrecision, secondary=_REL_PRODUCEDTIME_DATETIMEWITHPRECISION, uselist=False, backref='cyboxtime_produced')
  received_time = relationship(DateTimeWithPrecision, secondary=_REL_RECEIVEDTIME_DATETIMEWITHPRECISION, uselist=False, backref='cyboxtime_received')

  informationsource_id = Column(BigIntegerType, ForeignKey('informationsources.informationsource_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

  _PARENTS = ['information_source']

  def to_dict(self, cache_object):
    result = {'start_time': self.attribute_to_dict(self.start_time, cache_object),
              'end_time':self.attribute_to_dict(self.end_time, cache_object),
              'produced_time':self.attribute_to_dict(self.produced_time, cache_object),
              'received_time':self.attribute_to_dict(self.received_time, cache_object),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
