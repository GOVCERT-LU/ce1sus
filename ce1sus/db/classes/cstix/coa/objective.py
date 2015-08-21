# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.coa.relations import _REL_OBJECTIVE_STRUCTUREDTEXT, _REL_OBJECTIVE_SHORT_STRUCTUREDTEXT, _REL_OBJECTIVE_CONFIDENCE
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Objective(Entity, Base):
  description = relationship('StructuredText', secondary=_REL_OBJECTIVE_STRUCTUREDTEXT, uselist=False)
  short_description = relationship('StructuredText', secondary=_REL_OBJECTIVE_SHORT_STRUCTUREDTEXT, uselist=False)
  applicability_confidence = relationship('Confidence', secondary=_REL_OBJECTIVE_CONFIDENCE, uselist=False)
  courseofaction_id = Column('courseofaction_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)

  coa = relationship('CourseOfAction', uselist=False)

  _PARENTS = ['coa']

  def to_dict(self, cache_object):
    if cache_object.complete:
      result = {
                'description': self.attribute_to_dict(self.description, cache_object),
                'short_description': self.attribute_to_dict(self.short_description, cache_object),
                'applicability_confidence': self.attribute_to_dict(self.applicability_confidence, cache_object),
                }
    else:
      result = {}

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
