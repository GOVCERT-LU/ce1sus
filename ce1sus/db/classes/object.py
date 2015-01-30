# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, Unicode

from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Properties, ValueException
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RelatedObject(Base):
  parent_id = Column('parent_id', Unicode(40), ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  parent = relationship('Object', primaryjoin='RelatedObject.parent_id==Object.identifier', uselist=False)
  child_id = Column('child_id', Unicode(40), ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  relation = Column('relation', Unicode(40))
  object = relationship('Object', primaryjoin='RelatedObject.child_id==Object.identifier', uselist=False)

  def to_dict(self, complete=True, inflated=False, event_permissions=None):
    # flatten related object
    obj = self.object.to_dict(complete, inflated, event_permissions)
    obj['relation'] = self.convert_value(self.relation)
    obj['parent_object_id'] = self.convert_value(self.parent_id)
    return {'identifier': self.convert_value(self.identifier),
            'object': obj,
            'relation': self.convert_value(self.relation),
            'parent_id': self.convert_value(self.parent_id)
            }

  def validate(self):
    # TODO: validate
    return True


class Object(ExtendedLogingInformations, Base):
  # rel_composition = relationship('ComposedObject')
  attributes = relationship('Attribute', lazy='dynamic')
  # if the composition is one the return the object (property)
  definition_id = Column('definition_id', Unicode(40), ForeignKey('objectdefinitions.objectdefinition_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)
  definition = relationship('ObjectDefinition', lazy='joined')

  related_objects = relationship('RelatedObject', primaryjoin='Object.identifier==RelatedObject.parent_id', lazy='dynamic')
  dbcode = Column('code', Integer, nullable=False, default=0)
  parent_id = Column('parent_id', Unicode(40), ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), index=True)
  parent = relationship('Observable', back_populates='object', primaryjoin='Object.parent_id==Observable.identifier', uselist=False)
  observable_id = Column('observable_id', Unicode(40), ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  observable = relationship('Observable', primaryjoin='Object.observable_id==Observable.identifier', uselist=False)

  @property
  def event(self):
    if self.observable:
      event = self.observable.parent
      return event
    else:
      raise ValueError(u'Parent of object was not set.')

  @property
  def event_id(self):
    if self.observable:
      return self.observable.parent_id
    else:
      raise ValueError(u'Parent of object was not set.')

  def validate(self):
    return True

  __bit_code = None

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

  def get_attributes_for_permissions(self, event_permissions):
    if event_permissions:
      if event_permissions.can_validate:
        return self.attributes.all()
      else:
        # count validated ones
        return self.attributes.filter(Attribute.dbcode.op('&')(1) == 1).all()
    else:
      # count shared and validated
      return self.attributes.filter(Attribute.dbcode.op('&')(3) == 3).all()

  def get_related_objects_for_permissions(self, event_permissions):
    if event_permissions:
      if event_permissions.can_validate:
        return self.related_objects.all()
      else:
        # count validated ones
        return self.related_objects.filter(Object.dbcode.op('&')(1) == 1).all()
    else:
      # count shared and validated
      return self.related_objects.filter(Object.dbcode.op('&')(3) == 3).all()

  def attributes_count_for_permissions(self, event_permissions):
    if event_permissions:
      if event_permissions.can_validate:
        return self.attributes.count()
      else:
        # count validated ones
        return self.attributes.filter(Attribute.dbcode.op('&')(1) == 1).count()
    else:
      # count shared and validated
      return self.attributes.filter(Attribute.dbcode.op('&')(3) == 3).count()

  def attribute_count(self):
    return self.attributes.count()

  def related_objects_count_for_permissions(self, event_permissions):
    if event_permissions:
      if event_permissions.can_validate:
        return self.related_objects.count()
      else:
        # count validated ones
        return self.related_objects.filter(Object.dbcode.op('&')(1) == 1).count()
    else:
      # count shared and validated
      return self.related_objects.filter(Object.dbcode.op('&')(3) == 3).count()

  def related_object_count(self):
    return self.related_objects.count()

  def to_dict(self, complete=True, inflated=False, event_permissions=None):
    attributes = list()
    for attribute in self.get_attributes_for_permissions(event_permissions):
      attributes.append(attribute.to_dict(complete, inflated, event_permissions))
    related = list()

    if attributes:
      attributes_count = len(attributes)
    else:
      attributes_count = self.attributes_count_for_permissions(event_permissions)

    if inflated:
      for related_object in self.get_related_objects_for_permissions(event_permissions):
        related.append(related_object.to_dict(complete, inflated, event_permissions))
      related_count = len(related)
    else:
      related_count = self.related_objects_count_for_permissions(event_permissions)

    return {'identifier': self.convert_value(self.identifier),
            'definition_id': self.convert_value(self.definition_id),
            'definition': self.definition.to_dict(complete, inflated),
            'attributes': attributes,
            'attributes_count': attributes_count,
            'creator_group': self.creator_group.to_dict(complete, inflated),
            'created_at': self.convert_value(self.created_at),
            'modified_on': self.convert_value(self.modified_on),
            'modifier_group': self.convert_value(self.modifier.group.to_dict(complete, inflated)),
            'related_objects': related,
            'related_objects_count': related_count,
            'properties': self.properties.to_dict(),
            'observable_id': self.convert_value(self.observable_id)
            }

  def populate(self, json):
    # TODO: if inflated
    definition_id = json.get('definition_id', None)
    if not definition_id:
      definition = json.get('definition', None)
      if definition:
        definition_id = definition.get('identifier', None)
    if self.definition_id:
      if self.definition_id != definition_id:
        raise ValueException(u'Object definitions cannot be updated')
    self.definition_id = definition_id
    self.properties.populate(json.get('properties', None))
