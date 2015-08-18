# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Relation(BaseObject, Base):
  """
  Container class for event relations
  """
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  event = relationship("Event", uselist=False,
                       primaryjoin='Event.identifier==Relation.event_id')
  rel_event_id = Column('rel_event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  rel_event = relationship("Event",
                           uselist=False,
                           primaryjoin='Event.identifier==Relation.rel_event_id')
  attribute_id = Column('attribute_id', BigIntegerType, ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  attribute = relationship("Attribute",
                           uselist=False,
                           primaryjoin='Attribute.identifier==Relation.attribute_id')
  rel_attribute_id = Column('rel_attribute_id', BigIntegerType, ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  rel_attribute = relationship('Attribute',
                               uselist=False,
                               primaryjoin='Attribute.identifier==Relation.rel_attribute_id')

  UniqueConstraint('event_id', 'attribute_id', 'rel_event_id', 'rel_attribute_id')

  def to_dict(self, cache_object):
    result = {
            'event': self.attribute_to_dict(self.event, cache_object),
            'rel_event': self.attribute_to_dict(self.rel_event, cache_object),
            'attribute': self.attribute_to_dict(self.attribute, cache_object),
            'rel_attribute': self.attribute_to_dict(self.rel_attribute, cache_object),
            }

    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)


  def validate(self):
    """
    Returns true if the object is valid
    """
    return True
