# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer, Unicode, Text, BIGINT

from ce1sus.db.classes.base import ExtendedLogingInformations
from ce1sus.db.classes.common import Properties
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


class ObjectBase(ExtendedLogingInformations):

  @declared_attr
  def parent_id(self):
    return Column('parent_id',
                  BIGINT,
                  ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), index=True)

  @declared_attr
  def parent(self):
    return relationship('Object',
                        uselist=False,
                        primaryjoin='Object.parent_id==Object.identifier')

  @declared_attr
  def children(self):
    return relationship('Object',
                        primaryjoin='Object.identifier==Object.parent_id')

  @declared_attr
  def event_id(self):
    return Column('parentEvent', BIGINT, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True)

  @declared_attr
  def event(self):
    return relationship('Event',
                        uselist=False,
                        primaryjoin='Event.identifier==Object.event_id')

  @declared_attr
  def dbcode(self):
    return Column('code', Integer)

  __bit_code = None

  @declared_attr
  def relation_id(self):
    return Column('relation_id', Integer)

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


class ComposedObject(ObjectBase, Base):
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


class Object(ObjectBase, Base):
  title = Column('title', Unicode(45), index=True, unique=True, nullable=False)
  description = Column('description', Text)
  sighting = Column('sighting', Integer, default=1, nullable=False)
  # relationship of ObservableComposition one to many
  rel_composition = relationship('ObservableComposition')
  rel_attributes = relationship('Attribute')
  operator_id = Column('operator_id', Integer(1), default=None)
  # if the composition is one the return the object (property)
  definition_id = Column('definition_id', BIGINT, ForeignKey('objectdefinitions.objectdefinition_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)
  definition = relationship(ObjectDefinition)
  type_id = Column('type_id', Integer(1))

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
