# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode

from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Relation(Base):
  """
  Container class for event relations
  """
  __tablename__ = 'EventRelations'
  event_id = Column(Unicode(40), ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  event = relationship("Event", uselist=False,
                       primaryjoin='Event.identifier==Relation.event_id')
  rel_event_id = Column(Unicode(40), ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  rel_event = relationship("Event",
                           uselist=False,
                           primaryjoin='Event.identifier==Relation.rel_event_id',
                           lazy='joined')
  attribute_id = Column(Unicode(40), ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  attribute = relationship("Attribute",
                           uselist=False,
                           primaryjoin='Attribute.identifier==Relation.attribute_id')
  rel_attribute_id = Column(Unicode(40), ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  rel_attribute = relationship("Attribute",
                               uselist=False,
                               primaryjoin='Attribute.identifier==Relation.rel_attribute_id',
                               lazy='joined')

  def validate(self):
    """
    Returns true if the object is valid
    """
    return self
