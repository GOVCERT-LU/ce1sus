# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.vocabs import ImpactRating
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class DirectImpactSummary(Entity, Base):
  asset_losses_id = Column('asset_losses_id', Integer, default=None)
  business_mission_disruption_id = Column('business_mission_disruption_id', Integer, default=None)
  response_and_recovery_costs_id = Column('response_and_recovery_costs_di', Integer, default=None)

  impact_assessment_id = Column('impactassessment_id', BigIntegerType, ForeignKey('impactassessments.impactassessment_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  __asset_losses = None

  _PARENTS = ['impact_assessment']

  @property
  def asset_losses(self):
    if not self.__asset_losses:
      if self.asset_losses_id:
        self.__asset_losses = ImpactRating(self, 'asset_losses_id')
      else:
        return None
    return self.__asset_losses.name

  @asset_losses.setter
  def asset_losses(self, value):
    if not self.asset_losses:
      self.__asset_losses = ImpactRating(self, 'asset_losses_id')
    self.asset_losses.name = value

  __business_mission_disruption = None

  @property
  def business_mission_disruption(self):
    if not self.__business_mission_disruption:
      if self.business_mission_disruption_id:
        self.__business_mission_disruption = ImpactRating(self, 'business_mission_disruption_id')
      else:
        return None
    return self.__business_mission_disruption.name

  @business_mission_disruption.setter
  def business_mission_disruption(self, value):
    if not self.business_mission_disruption:
      self.__business_mission_disruption = ImpactRating(self, 'business_mission_disruption_id')
    self.business_mission_disruption.name = value

  __response_and_recovery_costs = None

  @property
  def response_and_recovery_costs(self):
    if not self.__response_and_recovery_costs:
      if self.response_and_recovery_costs_id:
        self.__response_and_recovery_costs = ImpactRating(self, 'response_and_recovery_costs_id')
      else:
        return None
    return self.__response_and_recovery_costs.name

  @response_and_recovery_costs.setter
  def response_and_recovery_costs(self, value):
    if not self.response_and_recovery_costs:
      self.__response_and_recovery_costs = ImpactRating(self, 'response_and_recovery_costs_id')
    self.response_and_recovery_costs.name = value

  def to_dict(self, cache_object):

    result = {
              'asset_losses': self.convert_value(self.asset_losses),
              'business_mission_disruption': self.convert_value(self.business_mission_disruption),
              'response_and_recovery_costs': self.convert_value(self.response_and_recovery_costs),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
