# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 28, 2015
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_ATTACKPATTERN_STRUCTUREDTEXT = Table('rel_attackpattern_structuredtext', getattr(Base, 'metadata'),
                                       Column('rist_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('attackpattern_id',
                                              BigIntegerType,
                                              ForeignKey('attackpatterns.attackpattern_id',
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

_REL_ATTACKPATTERN_STRUCTUREDTEXT_SHORT = Table('rel_attackpattern_structuredtext_short', getattr(Base, 'metadata'),
                                       Column('rist_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('attackpattern_id',
                                              BigIntegerType,
                                              ForeignKey('attackpatterns.attackpattern_id',
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

class AttackPattern(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{3}'.format(self.namespace, self.__class__.__name__, self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)

  _PARENTS = ['behaviour']

  title = Column('title', UnicodeType(255), index=True, nullable=True)
  description = relationship(StructuredText, secondary=_REL_ATTACKPATTERN_STRUCTUREDTEXT, uselist=False, backref='attack_pattern_description')
  short_description = relationship(StructuredText, secondary=_REL_ATTACKPATTERN_STRUCTUREDTEXT_SHORT, uselist=False, backref='attack_pattern_short_description')
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
