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
  object = relationship('Object', primaryjoin='RelatedObject.child_id==Object.identifier', uselist=False)

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.identifier),
            'object': self.object.to_dict(complete, inflated),
            'relation': self.convert_value(self.relation)
            }


class Object(ExtendedLogingInformations, Base):
  # rel_composition = relationship('ComposedObject')
  attributes = relationship('Attribute', lazy='joined')
  # if the composition is one the return the object (property)
  definition_id = Column('definition_id', Unicode(40), ForeignKey('objectdefinitions.objectdefinition_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)
  definition = relationship('ObjectDefinition', lazy='joined')

  related_objects = relationship('RelatedObject', primaryjoin='Object.identifier==RelatedObject.parent_id', lazy='joined')
  dbcode = Column('code', Integer)
  parent_id = Column('parent_id', Unicode(40), ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), index=True)
  parent = relationship('Observable', back_populates='object', uselist=False)

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

  def __attributes_count(self):
      return self._sa_instance_state.session.query(Attribute).filter(Attribute.object_id == self.identifier).count()

  def __rel_obj_count(self):
      return self._sa_instance_state.session.query(RelatedObject).filter(RelatedObject.parent_id == self.identifier).count()

  def to_dict(self, complete=True, inflated=False):
    attributes = list()
    for attribute in self.attributes:
      attributes.append(attribute.to_dict(complete, inflated))
    related = list()

    if attributes:
      attributes_count = len(attributes)
    else:
      attributes_count = self.__attributes_count()

    if inflated:
      for related_object in self.related_objects:
        related.append(related_object.to_dict(complete, inflated))
      related_count = len(related)
    else:
      related_count = self.__rel_obj_count()

    return {'identifier': self.convert_value(self.identifier),
            'definition': self.definition.to_dict(complete, inflated),
            'attributes': attributes,
            'attributes_count': attributes_count,
            'creator_group': self.creator_group.to_dict(complete, inflated),
            'created_at': self.convert_value(self.created_at),
            'modified_on': self.convert_value(self.modified_on),
            'modifier_group': self.convert_value(self.modifier.group.to_dict(complete, inflated)),
            'related_objects': related,
            'related_objects_count': related_count
            }

  def populate(self, json):
    # TODO: if inflated
    self.definition_id = json.get('definition_id', None)
