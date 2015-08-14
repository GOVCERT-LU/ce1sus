# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.vocabs import SecurityCompromise
from ce1sus.db.classes.internal.core import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class IndirectImpactSummary(Entity, Base):
  loss_of_competitive_advantage_id = Column(Integer)
  impact_assessment_id = Column('impactassessment_id', BigIntegerType, ForeignKey('impactassessments.impactassessment_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  __loss_of_competitive_advantage = None

  @property
  def loss_of_competitive_advantage(self):
    if not self.__loss_of_competitive_advantage:
      if self.loss_of_competitive_advantage_id:
        self.__loss_of_competitive_advantage = SecurityCompromise(self, 'loss_of_competitive_advantage_id')
    return self.__loss_of_competitive_advantage

  @loss_of_competitive_advantage.setter
  def loss_of_competitive_advantage(self, value):
    if not self.loss_of_competitive_advantage:
      self.__loss_of_competitive_advantage = SecurityCompromise(self, 'loss_of_competitive_advantage_id')
    self.loss_of_competitive_advantage.name = value

  brand_and_market_damage_id = Column(Integer)
  __brand_and_market_damage = None

  @property
  def brand_and_market_damage(self):
    if not self.__brand_and_market_damage:
      if self.brand_and_market_damage_id:
        self.__brand_and_market_damage = SecurityCompromise(self, 'brand_and_market_damage_id')
    return self.__brand_and_market_damage

  @brand_and_market_damage.setter
  def brand_and_market_damage(self, value):
    if not self.brand_and_market_damage:
      self.__brand_and_market_damage = SecurityCompromise(self, 'brand_and_market_damage_id')
    self.brand_and_market_damage.name = value

  increased_operating_costs_id = Column(Integer)
  __increased_operating_costs = None

  @property
  def increased_operating_costs(self):
    if not self.__increased_operating_costs:
      if self.increased_operating_costs_id:
        self.__increased_operating_costs = SecurityCompromise(self, 'increased_operating_costs_id')
    return self.__increased_operating_costs

  @increased_operating_costs.setter
  def increased_operating_costs(self, value):
    if not self.increased_operating_costs:
      self.__increased_operating_costs = SecurityCompromise(self, 'increased_operating_costs_id')
    self.increased_operating_costs.name = value

  legal_and_regulatory_costs_id = Column(Integer)
  __legal_and_regulatory_costs = None

  @property
  def legal_and_regulatory_costs(self):
    if not self.__legal_and_regulatory_costs:
      if self.legal_and_regulatory_costs_id:
        self.__legal_and_regulatory_costs = SecurityCompromise(self, 'legal_and_regulatory_costs_id')
    return self.__legal_and_regulatory_costs

  @legal_and_regulatory_costs.setter
  def legal_and_regulatory_costs(self, value):
    if not self.legal_and_regulatory_costs:
      self.__legal_and_regulatory_costs = SecurityCompromise(self, 'legal_and_regulatory_costs_id')
    self.legal_and_regulatory_costs.name = value

  @property
  def parent(self):
    return self.impact_assessment

  def to_dict(self, cache_object):

    result = {
              'loss_of_competitive_advantage': self.convert_value(self.loss_of_competitive_advantage),
              'brand_and_market_damage': self.convert_value(self.brand_and_market_damage),
              'increased_operating_costs': self.convert_value(self.increased_operating_costs),
              'legal_and_regulatory_costs': self.convert_value(self.legal_and_regulatory_costs),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
