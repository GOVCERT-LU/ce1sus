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
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_KILLCHAIN_PHASE = Table('rel_killchain_killchainphase', getattr(Base, 'metadata'),
                        Column('rkk_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                        Column('killchain_id', BigIntegerType, ForeignKey('killchains.killchain_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True),
                        Column('killchainphase_id', BigIntegerType, ForeignKey('killchainphases.killchainphase_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
                        )


class Killchain(Entity, Base):
  name = Column('name', UnicodeType(255))
  reference = Column('reference', UnicodeType(255))
  definer = Column('definer', UnicodeType(255))


  @property
  def number_of_phases(self):
    return len(self.kill_chain_phases)

  kill_chain_phases = relationship('KillChainPhase', secondary=_REL_KILLCHAIN_PHASE, backref='killchain')

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'name': self.convert_value(self.name),
                'reference': self.convert_value(self.reference),
                'definer': self.convert_value(self.definer),
                'number_of_phases': self.convert_value(self.number_of_phases),
                'kill_chain_phases': self.attributelist_to_dict(self.kill_chain_phases, cache_object)
                }
    else:
      result = {
                'name': self.convert_value(self.name),
                'reference': self.convert_value(self.reference),
                'definer': self.convert_value(self.definer),
                'number_of_phases': self.convert_value(self.number_of_phases),
                }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class KillChainPhase(Entity, Base):
  phase_ref = Column('phase_ref', Integer)
  name = Column('name', UnicodeType(255))
  ordinality = Column('ordinality', Integer)
  phase_id = Column('phase_id', Integer)

  def to_dict(self, cache_object):
    result = {
              'phase_ref': self.convert_value(self.phase_ref),
              'name': self.convert_value(self.name),
              'ordinality': self.convert_value(self.ordinality),
              }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class KillChainPhaseReference(Entity, Base):
  phase_ref = Column('phase_ref', Integer)
  name = Column('name', UnicodeType(255))
  ordinality = Column('ordinality', Integer)
  phase_id = Column('phase_id', Integer)

  kill_chain_id = Column('kill_chain_id', UnicodeType(255))
  kill_chain_name = Column('kill_chain_name', UnicodeType(255))
  ttp_id = Column(BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)

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
