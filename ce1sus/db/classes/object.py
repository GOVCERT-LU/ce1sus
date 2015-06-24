# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""

from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer, BigInteger

from ce1sus.common.checks import is_object_viewable
from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Properties, ValueException, TLP
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RelatedObject(Base):
  parent_id = Column('parent_id', BigInteger, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  parent = relationship('Object', primaryjoin='RelatedObject.parent_id==Object.identifier', uselist=False)
  child_id = Column('child_id', BigInteger, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  relation = Column('relation', BigInteger)
  object = relationship('Object', primaryjoin='RelatedObject.child_id==Object.identifier', uselist=False, lazy='joined', backref='related_object_parent')

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
        # flatten related object
    obj = self.object.to_dict(complete, inflated, event_permissions, user)
    obj['relation'] = self.convert_value(self.relation)
    obj['parent_object_id'] = self.convert_value(self.parent_id)
    return {'identifier': self.convert_value(self.uuid),
            'object': obj,
            'relation': self.convert_value(self.relation),
            'parent_id': self.convert_value(self.parent_id)
            }

  def validate(self):
    # TODO: validate
    return True


class Object(ExtendedLogingInformations, Base):
  # attributes = relationship('Attribute', lazy='dynamic')
  attributes = relationship('Attribute', lazy='joined')
  # if the composition is one the return the object (property)
  definition_id = Column('definition_id', BigInteger, ForeignKey('objectdefinitions.objectdefinition_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)
  definition = relationship('ObjectDefinition', lazy='joined')

  # related_objects = relationship('RelatedObject', primaryjoin='Object.identifier==RelatedObject.parent_id', lazy='dynamic')
  related_objects = relationship('RelatedObject', primaryjoin='Object.identifier==RelatedObject.parent_id', lazy='joined')
  dbcode = Column('code', Integer, nullable=False, default=0, index=True)
  parent_id = Column('parent_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), index=True)
  parent = relationship('Observable', back_populates='object', primaryjoin='Object.parent_id==Observable.identifier', uselist=False)
  observable_id = Column('observable_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), index=True, nullable=False)
  observable = relationship('Observable', primaryjoin='Object.observable_id==Observable.identifier', uselist=False)

  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """

    return TLP.get_by_id(self.tlp_level_id)

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    self.tlp_level_id = TLP.get_by_value(text)

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

  def get_attributes_for_permissions(self, event_permissions, user):
    attributes = list()
    for attribute in self.attributes:
      if is_object_viewable(attribute, event_permissions, user):
        attributes.append(attribute)
      else:
        if attribute.originating_group_id == user.group.identifier:
          attributes.append(attribute)
    return attributes


  def get_related_objects_for_permissions(self, event_permissions, user):

    rel_objs = list()
    for rel_obj in self.related_objects:
      if is_object_viewable(rel_obj.object, event_permissions, user):
        rel_objs.append(rel_obj)
    return rel_objs


  def attributes_count_for_permissions(self, event_permissions, user=None):

    return len(self.get_attributes_for_permissions(event_permissions, user))

  def attribute_count(self):
    return len(self.attributes)
    # return self.attributes.count()

  def related_objects_count_for_permissions(self, event_permissions, user=None):
    return len(self.get_related_objects_for_permissions(event_permissions, user))


  def related_object_count(self):
    return len(self.related_objects)
    # return self.related_objects.count()

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    attributes = list()
    if self.observable:
      uuid = self.convert_value(self.observable.uuid)
    else:
      uuid = self.convert_value(self.parent.uuid)

    for attribute in self.get_attributes_for_permissions(event_permissions, user):
      attributes.append(attribute.to_dict(complete, inflated, event_permissions, user))
    related = list()

    if attributes:
      attributes_count = len(attributes)
    else:
      attributes_count = self.attributes_count_for_permissions(event_permissions, user)

    if inflated:
      for related_object in self.get_related_objects_for_permissions(event_permissions, user):
        related.append(related_object.to_dict(complete, inflated, event_permissions, user))
      related_count = len(related)
    else:
      related_count = self.related_objects_count_for_permissions(event_permissions, user)
    if complete:
      return {'identifier': self.convert_value(self.uuid),
              'definition_id': self.convert_value(self.definition.uuid),
              'definition': self.definition.to_dict(complete, False),
              'attributes': attributes,
              'attributes_count': attributes_count,
              'creator_group': self.creator_group.to_dict(complete, inflated),
              'created_at': self.convert_value(self.created_at),
              'modified_on': self.convert_value(self.modified_on),
              'modifier_group': self.modifier.group.to_dict(complete, False),
              'related_objects': related,
              'related_objects_count': related_count,
              'properties': self.properties.to_dict(),
              'tlp': self.convert_value(self.tlp),
              'observable_id': uuid
              }
    else:
      return {'identifier': self.convert_value(self.uuid),
              'definition_id': self.convert_value(self.definition.uuid),
              'definition': self.definition.to_dict(complete, False),
              'attributes_count': attributes_count,
              'creator_group': self.creator_group.to_dict(complete, inflated),
              'created_at': self.convert_value(self.created_at),
              'modified_on': self.convert_value(self.modified_on),
              'modifier_group': self.modifier.group.to_dict(complete, False),
              'related_objects': related,
              'related_objects_count': related_count,
              'properties': self.properties.to_dict(),
              'tlp': self.convert_value(self.tlp),
              'observable_id': uuid
              }

  def populate(self, json, rest_insert=True):
    definition_uuid = json.get('definition_id', None)
    if not definition_uuid:
      definition = json.get('definition', None)
      if definition:
        definition_uuid = definition.get('identifier', None)
    if self.definition:
      if self.definition.uuid != definition_uuid:
        raise ValueException(u'Object definitions cannot be updated')

    self.properties.populate(json.get('properties', None))
    self.properties.is_rest_instert = rest_insert
    self.properties.is_web_insert = not rest_insert
    self.tlp = json.get('tlp', 'Amber').title()
