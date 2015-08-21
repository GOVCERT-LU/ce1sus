# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 28, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.campaign.relations import _REL_CAMPAIGN_INTENDEDEFFECT
from ce1sus.db.classes.cstix.common.vocabs import IntendedEffect as VocabIntendedEffect
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base
from ce1sus.db.classes.cstix.incident.relations import _REL_INCIDENT_INTENDED_EFFECT
from ce1sus.db.classes.cstix.threat_actor.relations import _REL_THREATACTOR_INTENDED_EFFECT
from ce1sus.db.classes.cstix.ttp.relations import _REL_TTP_INTENDED_EFFECT


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class IntendedEffect(Entity, Base):

  campaign_id = Column('campaign_id', BigIntegerType, ForeignKey('campaigns.campaign_id', ondelete='cascade', onupdate='cascade'), index=True)
  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), index=True)
  threatactor_id = Column('threatactor_id', BigIntegerType, ForeignKey('threatactors.threatactor_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  effect_id = Column('effect_id', Integer)
  __effect = None

  campaign = relationship('Campaign', secondary=_REL_CAMPAIGN_INTENDEDEFFECT, uselist=False)
  incident = relationship('Incident', uselist=False, secondary=_REL_INCIDENT_INTENDED_EFFECT)
  threat_actor = relationship('ThreatActor', uselist=False, secondary=_REL_THREATACTOR_INTENDED_EFFECT)
  ttp = relationship('TTP', uselist=False, secondary=_REL_TTP_INTENDED_EFFECT)

  _PARENTS = ['campaign',
              'ttp',
              'threat_actor',
              'incident', ]

  @property
  def effect(self):
    if not self.__effect:
      if self.effect_id:
        self.__effect = VocabIntendedEffect(self, 'effect_id')
      else:
        return None
    return self.__effect.name

  @effect.setter
  def effect(self, value):
    if not self.effect:
      self.__effect = VocabIntendedEffect(self, 'effect_id')
    self.effect.name = value

  @property
  def intendedeffect(self):
    return self.effect

  @intendedeffect.setter
  def intendedeffect(self, intendedeffect):
    self.effect = intendedeffect

  def to_dict(self, cache_object):
    result = {
              'effect':self.convert_value(self.effect),
             }
    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
