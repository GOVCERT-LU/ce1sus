# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 28, 2015
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.ttp.relations import _REL_ATTACKPATTERN_STRUCTUREDTEXT, _REL_ATTACKPATTERN_STRUCTUREDTEXT_SHORT
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class AttackPattern(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{3}'.format(self.namespace, self.__class__.__name__, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  _PARENTS = ['behavior']
  behavior = relationship('Behavior', uselist=False)

  title = Column('title', UnicodeType(255), index=True, nullable=True)
  description = relationship(StructuredText, secondary=_REL_ATTACKPATTERN_STRUCTUREDTEXT, uselist=False)
  short_description = relationship(StructuredText, secondary=_REL_ATTACKPATTERN_STRUCTUREDTEXT_SHORT, uselist=False)
  behavior_id = Column('behavior_id', BigIntegerType, ForeignKey('behaviors.behavior_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  capec_id = Column('capec_id', UnicodeTextType())

  def to_dict(self, cache_object):

    result = {
              'id_': self.convert_value(self.id_),
              'description': self.attribute_to_dict(self.description, cache_object),
              'short_description': self.attribute_to_dict(self.short_description, cache_object),
              'title': self.convert_value(self.title)
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
