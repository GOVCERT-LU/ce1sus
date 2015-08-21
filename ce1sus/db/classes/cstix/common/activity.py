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
from ce1sus.db.classes.cstix.common.relations import _REL_ACTIVITY_STRUCTUREDTEXT, _REL_ACTIVITY_DATETIMEWITHPRECISION
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Activity(Entity, Base):

  description = relationship('StructuredText', secondary=_REL_ACTIVITY_STRUCTUREDTEXT, uselist=False)
  date_time = relationship(DateTimeWithPrecision, secondary=_REL_ACTIVITY_DATETIMEWITHPRECISION, uselist=False)
  campaign_id = Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True)

  campaign = relationship('Campaign', uselist=False)

  _PARENTS = ['campaign']

  def to_dict(self, cache_object):

    result = {'description': self.attribute_to_dict(self.description, cache_object),
            'date_time': self.attribute_to_dict(self.date_time, cache_object)
            }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
