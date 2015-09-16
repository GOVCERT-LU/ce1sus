# -*- coding: utf-8 -*-

"""
(Description)

Created on 15 Sep 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer

from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.corebase import UnicodeType, BigIntegerType
from ce1sus.db.common.session import Base
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.ccybox.common.relations import _REL_MEASURESOURCE_STRUCTUREDTEXT


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MeasureSource(Entity, Base):
  class_ = Column('class', UnicodeType(255))
  source_type = Column('source_type', UnicodeType(255))
  name = Column('name', UnicodeType(255))
  sighting_count = Column('sighting_count', Integer)
  information_source_type = Column('information_source_type', UnicodeType(255))
  tool_type =  Column('tool_type', UnicodeType(255))
  description = relationship(StructuredText, uselist=False, secondary=_REL_MEASURESOURCE_STRUCTUREDTEXT)
  contributors = None
  time = None
  tools = None
  platform = None
  system = None
  instance = None

  _PARENTS = ['observable']

  observable_id = Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  observable = relationship('Observable', uselist=False)
