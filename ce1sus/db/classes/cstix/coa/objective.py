# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 27, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table, Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.confidence import Confidence
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.corebase import BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_OBJECTIVE_STRUCTUREDTEXT = Table('rel_objective_structuredtext', getattr(Base, 'metadata'),
                                      Column('ros_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                      Column('objective_id',
                                             BigIntegerType,
                                             ForeignKey('objectives.objective_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                             index=True,
                                             nullable=False),
                                      Column('structuredtext_id',
                                             BigIntegerType,
                                                     ForeignKey('structuredtexts.structuredtext_id',
                                                                ondelete='cascade',
                                                                onupdate='cascade'),
                                             index=True,
                                             nullable=False)
                                      )

_REL_OBJECTIVE_SHORT_STRUCTUREDTEXT = Table('rel_objective_short_structuredtext', getattr(Base, 'metadata'),
                                            Column('ross_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                            Column('objective_id',
                                                   BigIntegerType,
                                                   ForeignKey('objectives.objective_id',
                                                              ondelete='cascade',
                                                              onupdate='cascade'),
                                                   index=True,
                                                   nullable=False),
                                            Column('structuredtext_id',
                                                   BigIntegerType,
                                                      ForeignKey('structuredtexts.structuredtext_id',
                                                                 ondelete='cascade',
                                                                 onupdate='cascade'),
                                                   nullable=False,
                                                   index=True)
                                            )

_REL_OBJECTIVE_CONFIDENCE = Table('rel_objective_confidence', getattr(Base, 'metadata'),
                                  Column('rss_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                  Column('objective_id',
                                         BigIntegerType,
                                         ForeignKey('objectives.objective_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         index=True,
                                         nullable=False),
                                  Column('confidence_id',
                                         BigIntegerType,
                                         ForeignKey('confidences.confidence_id',
                                                    ondelete='cascade',
                                                    onupdate='cascade'),
                                         nullable=False,
                                         index=True)
                                  )

class Objective(Entity, Base):
  description = relationship(StructuredText, secondary=_REL_OBJECTIVE_STRUCTUREDTEXT, uselist=False, backref='objective_description')
  short_description = relationship(StructuredText, secondary=_REL_OBJECTIVE_SHORT_STRUCTUREDTEXT, uselist=False, backref='objective_short_description')
  applicability_confidence = relationship(Confidence, secondary=_REL_OBJECTIVE_CONFIDENCE, uselist=False, backref='objective')
  courseofaction_id = Column('courseofaction_id', BigIntegerType, ForeignKey('courseofactions.courseofaction_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)

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
