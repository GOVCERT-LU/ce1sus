# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.data_marking import MarkingStructure
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class TLPMarkingStructure(MarkingStructure):
  # override identifier to keep the polymorphics
  identifier = Column(BigIntegerType, ForeignKey('markingstructures.markingstructure_id'), primary_key=True)
  color = Column('color', UnicodeType(20), nullable=False)

  __mapper_args__ = {'polymorphic_identity':'tlpmarkingstructure'}

  def to_dict(self, cache_object):

    result = {
              'color': self.convert_value(self.color)
              }

    parent_dict = MarkingStructure.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
