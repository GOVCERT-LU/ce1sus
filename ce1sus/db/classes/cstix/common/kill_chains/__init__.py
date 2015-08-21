# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Unicode, Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base
from ce1sus.db.classes.cstix.indicator.relations import _REL_INDICATOR_KILLCHAINPHASEREF
from ce1sus.db.classes.cstix.ttp.relations import _REL_TTP_KILLCHAINPHASE


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class KillChainPhaseReference(Entity, Base):
  phase_ref = Column('phase_ref', Integer)
  name = Column('name', UnicodeType(255))
  ordinality = Column('ordinality', Integer)
  phase_id = Column('phase_id', Integer)

  kill_chain_id = Column('kill_chain_id', UnicodeType(255))
  kill_chain_name = Column('kill_chain_name', UnicodeType(255))

  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_KILLCHAINPHASEREF)
  ttp = relationship('TTP', uselist=False, secondary=_REL_TTP_KILLCHAINPHASE)
  _PARENTS = ['ttp', 'indicator']

  def to_dict(self, cache_object):
    result = {
              'phase_ref': self.convert_value(self.phase_ref),
              'name': self.convert_value(self.name),
              'ordinality': self.convert_value(self.ordinality),
              'kill_chain_id': self.convert_value(self.kill_chain_id),
              'kill_chain_name': self.convert_value(self.kill_chain_name),
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
