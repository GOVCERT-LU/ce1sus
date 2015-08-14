# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.schema import Column
from sqlalchemy.types import Float

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.core import UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class LossEstimation(Entity, Base):
  iso_currency_code = Column('iso_currency_code', UnicodeType(3))
  amount = Column('amount', Float)

  @property
  def parent(self):
    if self.total_loss_estimation_ini:
      return self.total_loss_estimation_ini
    elif self.total_loss_estimation_act:
      return self.total_loss_estimation_act
    raise ValueError('Parent not found')

  def to_dict(self, cache_object):

    result = {
              'iso_currency_code': self.convert_value(self.iso_currency_code),
              'amount': self.convert_value(self.amount),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
