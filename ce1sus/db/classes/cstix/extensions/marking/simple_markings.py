# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 3, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.cstix.common.statement import Statement
from ce1sus.db.classes.cstix.data_marking import MarkingStructure, _REL_MARKINGSTRUCTURE_STATEMENT
from ce1sus.db.classes.internal.core import BigIntegerType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SimpleMarkingStructure(MarkingStructure):
  # override identifier to keep the polymorphics
  identifier = Column(BigIntegerType, ForeignKey('markingstructures.markingstructure_id'), primary_key=True)
  statement = relationship(Statement, secondary=_REL_MARKINGSTRUCTURE_STATEMENT)

  __mapper_args__ = {'polymorphic_identity':'simplemarkingstructure'}

  def to_dict(self, cache_object):

    result = {
              'statement': self.attribute_to_dict(self.statement, cache_object)
              }

    parent_dict = MarkingStructure.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
