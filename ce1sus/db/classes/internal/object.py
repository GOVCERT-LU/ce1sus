# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""

from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.common.vocabs import ObjectRelationship
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.core import BaseElement, BigIntegerType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Object(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.get_classname(), self.uuid)

  @id_.setter
  def id_(self, value):
    self.set_id(value)


  idref = Column(u'idref', UnicodeType(255), nullable=True, index=True)
  # properties
  related_objects = relationship('RelatedObject', primaryjoin='Object.identifier==RelatedObject.parent_id', lazy='joined')


  # ce1sus specific
  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  attributes = relationship('Attribute', lazy='joined')

  # if the composition is one the return the object (property)
  definition_id = Column('definition_id', BigIntegerType, ForeignKey('objectdefinitions.objectdefinition_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)
  definition = relationship('ObjectDefinition', lazy='joined')
  observable_id = Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  observable = relationship('Observable', primaryjoin='Object.observable_id==Observable.identifier', uselist=False)

  @property
  def event(self):
    if self.observable:
      event = self.observable.event
      return event
    else:
      raise ValueError(u'Parent of object was not set.')

  @property
  def event_id(self):
    if self.observable:
      return self.observable.event_id
    else:
      raise ValueError(u'Parent of object was not set.')

  def validate(self):
    return True
  
  @property
  def parent(self):
    if self.related_object_parent:
      return self.related_object_parent
    elif self.observable:
      return self.observable

  def to_dict(self, cache_object):
    if self.observable:
      uuid = self.convert_value(self.observable.uuid)
    else:
      uuid = self.convert_value(self.parent.uuid)

    result = {
            'definition_id': self.convert_value(self.definition.uuid),
            'definition': self.attribute_to_dict(self.definition, cache_object),
            'attributes': self.attributelist_to_dict(self.attributes, cache_object),
            'related_objects': self.attributelist_to_dict(self.related_objects, cache_object),
            'observable_id': uuid
            }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class RelatedObject(BaseElement, Base):
  parent_id = Column('parent_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child_id = Column('child_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  relationship_id = Column('relationship_id', Integer, nullable=True)
  idref = Column(u'idref', UnicodeType(255), nullable=True, index=True)

  object = relationship(Object, primaryjoin='RelatedObject.child_id==Object.identifier', uselist=False, backref='related_object_parent')

  __relationship = None

  @property
  def relationship(self):
    if not self.__relationship:
      # Note relationship can be none
      self.__relationship = ObjectRelationship(self, 'relationship_id')
    return self.__relationship

  @relationship.setter
  def relationship(self, relationship):
    if relationship:
      self.relationship.name = relationship
    else:
      self.relationship_id = None

  def to_dict(self, cache_object):
    obj = self.attribute_to_dict(self.object, cache_object)
    result = {
            'object': obj,
            'relationship': self.convert_value(self.relationship.name),
            'parent_id': self.convert_value(self.parent_id)
            }
    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

  def validate(self):
    # TODO: validate
    return True
