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
from ce1sus.db.classes.ccybox.core.relations import _REL_OBSERVABLE_OBJECT
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.internal.core import BaseElement
from ce1sus.db.classes.internal.corebase import UnicodeType, BigIntegerType
from ce1sus.db.classes.internal.relations import _REL_OBJECT_OBJECT
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
  related_objects = relationship('RelatedObject', primaryjoin='Object.identifier==RelatedObject.parent_id')
  # ce1sus specific
  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')
  attributes = relationship('Attribute')

  # if the composition is one the return the object (property)
  definition_id = Column('definition_id', BigIntegerType, ForeignKey('objectdefinitions.objectdefinition_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)
  definition = relationship('ObjectDefinition')
  observable = relationship('Observable', secondary=_REL_OBSERVABLE_OBJECT, uselist=False, back_populates='object')
  parent_id = Column('parent_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), index=True)
  db_object = None
  objects = relationship('Object', primaryjoin='Object.identifier==rel_object_object.c.parent_id', secondaryjoin='Object.identifier==rel_object_object.c.child_id', secondary=_REL_OBJECT_OBJECT)

  related_object = relationship('RelatedObject', primaryjoin='RelatedObject.child_id==Object.identifier', uselist=False)
  @property
  def event(self):
    return self.root

  @property
  def event_id(self):
    return self.event.identifier

  def validate(self):
    return True
  
  _PARENTS = ['observable', 'related_object']

  @property
  def object(self):
    return self.db_object[0]

  @object.setter
  def object(self, value):
    self.db_object = [value]
    
  @property
  def parent(self):
    if self.object:
      return object
    else:
      return self.get_parent()

  @parent.setter
  def parent(self, instance):
    if isinstance(instance, Object):
      self.object = instance
    else:
      self.set_parent(instance)

  def get_populated(self, cache_object):
    return self.get_instance([Object.definition], cache_object)

  def to_dict(self, cache_object):
    instance = self.get_populated(cache_object)

    cache_object_defs = cache_object.make_copy()
    cache_object_defs.inflated = False
    if cache_object.complete:
      result = {
              'definition_id': instance.convert_value(instance.definition.uuid),
              'definition': instance.attribute_to_dict(instance.definition, cache_object_defs),
              'attributes': instance.attributelist_to_dict('attributes', cache_object),
              'related_objects': instance.attributelist_to_dict('related_objects', cache_object),
              'objects': instance.attributelist_to_dict('objects', cache_object),
              }
    else:
      result = {
              'definition_id': instance.convert_value(instance.definition.uuid),
              'definition': instance.attribute_to_dict(instance.definition, cache_object_defs),
              }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

class RelatedObject(Entity, Base):
  parent_id = Column('parent_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  child_id = Column('child_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  relationship_id = Column('relationship_id', Integer, nullable=True)
  idref = Column(u'idref', UnicodeType(255), nullable=True, index=True)

  parent = relationship(Object, primaryjoin='RelatedObject.parent_id==Object.identifier', uselist=False)
  object = relationship(Object, primaryjoin='RelatedObject.child_id==Object.identifier', uselist=False)

  __relationship = None

  _PARENTS = ['parent']

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
    instance = self.get_instance([], cache_object)
    obj = self.attribute_to_dict(self.object, cache_object)
    result = {
            'object': obj,
            'relationship': instance.convert_value(instance.relationship.name),
            'parent_id': instance.convert_value(instance.parent_id)
            }
    parent_dict = BaseElement.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

  def validate(self):
    # TODO: validate
    return True
