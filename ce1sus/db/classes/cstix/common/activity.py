# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.datetimewithprecision import DateTimeWithPrecision
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_ACTIVITY_STRUCTUREDTEXT = Table('rel_activity_structuredtext', getattr(Base, 'metadata'),
                                     Column('ras_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                     Column('activity_id',
                                            BigIntegerType,
                                            ForeignKey('activitys.activity_id',
                                                       ondelete='cascade',
                                                       onupdate='cascade'),
                                            index=True,
                                            nullable=False),
                                     Column('structuredtext_id',
                                            BigIntegerType,
                                            ForeignKey('structuredtexts.structuredtext_id',
                                                       ondelete='cascade',
                                                       onupdate='cascade'),
                                            nullable=False,
                                            index=True)
                                     )

_REL_ACTIVITY_DATETIMEWITHPRECISION = Table('rel_activity_datetimewithprecision', getattr(Base, 'metadata'),
                                            Column('rad_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                            Column('activity_id',
                                                   BigIntegerType,
                                                   ForeignKey('activitys.activity_id',
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


class Activity(Entity, Base):

  description = relationship(StructuredText, secondary=_REL_ACTIVITY_STRUCTUREDTEXT, uselist=False)
  date_time = relationship(DateTimeWithPrecision, secondary=_REL_ACTIVITY_DATETIMEWITHPRECISION, uselist=False)
  campaign_id = Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True)

  def to_dict(self, cache_object):

    result = {'description': self.attribute_to_dict(self.description, cache_object),
            'date_time': self.attribute_to_dict(self.date_time, cache_object)
            }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
