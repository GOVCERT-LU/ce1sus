# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint
from sqlalchemy.types import BigInteger

from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Relation(Base):
  """
  Container class for event relations
  """
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  event = relationship("Event", uselist=False,
                       primaryjoin='Event.identifier==Relation.event_id')
  rel_event_id = Column('rel_event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  rel_event = relationship("Event",
                           uselist=False,
                           primaryjoin='Event.identifier==Relation.rel_event_id')
  attribute_id = Column('attribute_id', BigInteger, ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  attribute = relationship("Attribute",
                           uselist=False,
                           primaryjoin='Attribute.identifier==Relation.attribute_id')
  rel_attribute_id = Column('rel_attribute_id', BigInteger, ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  rel_attribute = relationship('Attribute',
                               uselist=False,
                               primaryjoin='Attribute.identifier==Relation.rel_attribute_id')

  UniqueConstraint('event_id', 'attribute_id', 'rel_event_id', 'rel_attribute_id')

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    return {'event': self.event.to_dict(complete, inflated, event_permissions, user),
            'rel_event': self.rel_event.to_dict(complete, inflated, event_permissions, user),
            'attribute': self.attribute.to_dict(complete, inflated, event_permissions, user),
            'rel_attribute': self.rel_attribute.to_dict(complete, inflated, event_permissions, user),
            }

  def validate(self):
    """
    Returns true if the object is valid
    """
    return True
