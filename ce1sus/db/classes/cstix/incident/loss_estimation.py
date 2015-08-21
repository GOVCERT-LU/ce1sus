# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column
from sqlalchemy.types import Float

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.incident.relations import _REL_TLE_INIT_LOSSESTIMATION, _REL_TLE_ACTU_LOSSESTIMATION
from ce1sus.db.classes.internal.corebase import UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class LossEstimation(Entity, Base):
  iso_currency_code = Column('iso_currency_code', UnicodeType(3))
  amount = Column('amount', Float)

  _PARENTS = ['total_loss_estimation_ini', 'total_loss_estimation_act']
  total_loss_estimation_ini = relationship('TotalLossEstimation', secondary=_REL_TLE_INIT_LOSSESTIMATION, uselist=False)
  total_loss_estimation_act = relationship('TotalLossEstimation', secondary=_REL_TLE_ACTU_LOSSESTIMATION, uselist=False)

  def to_dict(self, cache_object):

    result = {
              'iso_currency_code': self.convert_value(self.iso_currency_code),
              'amount': self.convert_value(self.amount),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
