# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.vocabs import ImpactQualification, IntendedEffect
from ce1sus.db.classes.cstix.incident.direct_impact_summary import DirectImpactSummary
from ce1sus.db.classes.cstix.incident.indirect_impact_summary import IndirectImpactSummary
from ce1sus.db.classes.cstix.incident.total_loss_estimation import TotalLossEstimation
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Effect(Entity, Base):
  eff_id = Column('eff_id', Integer, default=None, nullable=False)
  impactassessment_id = Column('impactassessment_id', BigIntegerType, ForeignKey('impactassessments.impactassessment_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  __value = None

  @property
  def value(self):
    if not self.__value:
      if self.status_id:
        self.__value = IntendedEffect(self, 'eff_id')
    return self.__value

  @value.setter
  def value(self, value):
    if not self.value:
      self.__value = IntendedEffect(self, 'eff_id')
    self.value.name = value

  def to_dict(self, cache_object):

    result = {
              'value': self.convert_value(self.value),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class ImpactAssessment(Entity, Base):
  direct_impact_summary = relationship(DirectImpactSummary, uselist=False)
  indirect_impact_summary = relationship(IndirectImpactSummary, uselist=False)
  total_loss_estimation = relationship(TotalLossEstimation, uselist=False)
  impact_qualification_id = Column(Integer)

  @property
  def impact_qualification(self):
    if not self.__impact_qualification:
      if self.impact_qualification_id:
        self.__impact_qualification = ImpactQualification(self, 'impact_qualification_id')
    return self.__impact_qualification

  @impact_qualification.setter
  def impact_qualification(self, impact_qualification):
    if not self.impact_qualification:
      self.__impact_qualification = ImpactQualification(self, 'impact_qualification_id')
    self.impact_qualification.name = impact_qualification

  effects = relationship(Effect)

  # ce1sus specific
  incident_id = Column('incident_id', BigIntegerType, ForeignKey('incidents.incident_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  def to_dict(self, cache_object):

    result = {
              'direct_impact_summary': self.attribute_to_dict(self.direct_impact_summary, cache_object),
              'indirect_impact_summary': self.attribute_to_dict(self.indirect_impact_summary, cache_object),
              'total_loss_estimation': self.attribute_to_dict(self.total_loss_estimation, cache_object),
              'impact_qualification': self.convert_value(self.impact_qualification),
              'effects': self.attributelist_to_dict(self.effects, cache_object)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
