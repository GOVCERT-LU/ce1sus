# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey
from sqlalchemy.types import DateTime, Unicode

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.names import Name
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_CAMPAIGNREF_NAME = Table('rel_campaingref_name', getattr(Base, 'metadata'),
                              Column('rct_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                              Column('campaignref_id', BigIntegerType, ForeignKey('campaignrefs.campaignref_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False),
                              Column('name_id', BigIntegerType, ForeignKey('names.name_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                              )


class CampaignRef(Entity, Base):

  # TODO: determine how to do this reference!?
  idref = Column('idref', UnicodeType(255), default=None)
  timestamp = Column('timestamp', DateTime, default=None)
  names = relationship(Name, secondary=_REL_CAMPAIGNREF_NAME)

  def to_dict(self, cache_object):

    result = {
              'idref': self.convert_value(self.idref),
              'timestamp': self.convert_value(self.timestamp),
              'names': self.attributelist_to_dict(self.names, cache_object)
            }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
