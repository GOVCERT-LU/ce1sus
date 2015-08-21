# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.incident.loss_estimation import LossEstimation
from ce1sus.db.classes.cstix.incident.relations import _REL_TLE_INIT_LOSSESTIMATION, _REL_TLE_ACTU_LOSSESTIMATION
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TotalLossEstimation(Entity, Base):
  initial_reported_total_loss_estimation = relationship(LossEstimation, secondary=_REL_TLE_INIT_LOSSESTIMATION, uselist=False)
  actual_total_loss_estimation = relationship(LossEstimation, secondary=_REL_TLE_ACTU_LOSSESTIMATION, uselist=False)
  impact_assessment_id = Column('impactassessment_id', BigIntegerType, ForeignKey('impactassessments.impactassessment_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)

  _PARENTS = ['impact_assessment']
  impact_assessment = relationship('ImpactAssessment', uselist=False)

  def to_dict(self, cache_object):

    result = {
              'initial_reported_total_loss_estimation': self.attribute_to_dict(self.initial_reported_total_loss_estimation, cache_object),
              'actual_total_loss_estimation': self.attribute_to_dict(self.actual_total_loss_estimation, cache_object)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
