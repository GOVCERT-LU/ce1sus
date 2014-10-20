# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, Unicode, Text, BIGINT

from ce1sus.db.classes.base import ExtendedLogingInformations
from ce1sus.db.classes.definitions import ObjectDefinition
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

_REL_OBJECT_OBJECT_ = Table(
    'composed_object_relations', getattr(Base, 'metadata'),
    Column('object_id', BIGINT, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade')),
    Column('composedobject_id', BIGINT, ForeignKey('composedobjects.composedobject_id', onupdate='cascade', ondelete='cascade'))
)


class ComposedObject(ExtendedLogingInformations, Base):
  operator_id = Column('operator_id', BIGINT, default=None)
  # one to many
  objects = relationship('Object')

  @hybrid_property
  def attributes_count(self):
    counter = 0
    for obj in self.objects:
      try:
        counter = counter + obj.attributes_count
      except ValueError:
        try:
          for comp_obj in obj.composition:
            counter = counter + comp_obj.attributes_count
        except ValueError:
          pass
    return counter


class Object(ExtendedLogingInformations, Base):
  title = Column('title', Unicode(45), index=True, unique=True, nullable=False)
  description = Column('description', Text)
  sighting = Column('sighting', Integer, default=1, nullable=False)
  # relationship of ObservableComposition one to many
  rel_composition = relationship('ObservableComposition')
  rel_attributes = relationship('Attribute')
  operator_id = Column('operator_id', Integer(1), default=None)
  # if the composition is one the return the object (property)
  definition_id = Column(BIGINT, ForeignKey('objectdefinitions.objectdefinition_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(ObjectDefinition)

  @hybrid_property
  def attributes_count(self):
      return len(self.attributes)

  @property
  def attributes(self):
    if self.rel_composition:
      raise ValueError(u'Object is already composed')
    else:
      return self.rel_attributes

  @attributes.setter
  def attributes(self, attributes):
    if self.rel_composition:
      raise ValueError(u'Object is already composed')
    else:
      self.rel_attributes = attributes

  @property
  def composition(self):
    if self.rel_attributes:
      raise ValueError(u'Object has already attributes')
    else:
      return self.rel_composition

  @composition.setter
  def composition(self, composition):
    if isinstance(composition, ComposedObject):
      if self.rel_attributes:
        raise ValueError(u'Object is already a composed object')
      else:
        self.rel_composition = composition
    else:
        raise ValueError(u'Value must be a ComposedObject')
