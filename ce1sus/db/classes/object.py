# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode, Boolean

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Properties
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RelatedObject(Base):
  parent_id = Column('parent_id', Unicode(40), ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child_id = Column('child_id', Unicode(40), ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  relation = Column('relation', Unicode(40))
  # TODO make this n:m -> less db space
  objects = relationship('Object', primaryjoin='RelatedObject.child_id==Object.identifier')


class Object(ExtendedLogingInformations, Base):
  # rel_composition = relationship('ComposedObject')
  attributes = relationship('Attribute')
  operator_id = Column('operator_id', Integer(1), default=None)
  # if the composition is one the return the object (property)
  definition_id = Column('definition_id', Unicode(40), ForeignKey('objectdefinitions.objectdefinition_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)
  definition = relationship('ObjectDefinition')
  type_id = Column('type_id', Integer(1))

  related_objects = relationship('RelatedObject', primaryjoin='Object.identifier==RelatedObject.parent_id')
  dbcode = Column('code', Integer)
  parent_id = Column('parent_id', Unicode(40), ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), index=True)
  parent = relationship('Observable', back_populates='object', uselist=False)
  __bit_code = None

  def validate(self):
    return True

  @property
  def properties(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = Properties('0', self)
      else:
        self.__bit_code = Properties(self.dbcode, self)
    return self.__bit_code

  @hybrid_property
  def attributes_count(self):
      return len(self.attributes)
