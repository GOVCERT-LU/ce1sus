# -*- coding: utf-8 -*-

"""
(Description)

Created on Jun 25, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.ttp.attack_pattern import AttackPattern
from ce1sus.db.classes.cstix.ttp.exploit import Exploit
from ce1sus.db.classes.cstix.ttp.malware_instance import MalwareInstance
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Behavior(Entity, Base):
  ttp_id = Column(BigIntegerType, ForeignKey('ttps.ttp_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  malware_instances = relationship(MalwareInstance)
  attack_patterns = relationship(AttackPattern)
  exploits = relationship(Exploit)

  _PARENTS = ['ttp']
  ttp = relationship('TTP', uselist=False)

  def to_dict(self, cache_object):

    result = {
              'malware_instances': self.attributelist_to_dict('malware_instances', cache_object),
              'attack_patterns': self.attributelist_to_dict('attack_patterns', cache_object),
              'exploits': self.attributelist_to_dict('exploits', cache_object)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
