# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 7, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import BigInteger, UnicodeText, Unicode, Boolean

from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ErrorMispAttribute(Base):

  object_id = Column('object_id', BigInteger, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'))
  object = relationship('Object', primaryjoin='Object.identifier==ErrorMispAttribute.object_id', lazy='joined', uselist=False)
  value = Column('value', UnicodeText)
  category = Column('category', Unicode(255))
  type_ = Column('type', Unicode(255))
  observable_id = Column('observable_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'))
  observable = relationship('Observable', primaryjoin='ErrorMispAttribute.observable_id==Observable.identifier', uselist=False)
  misp_id = Column('misp_id', Unicode(255))
  is_ioc = Column('is_ioc', Boolean)
  share = Column('share', Boolean)
  event = relationship('Event', uselist=False, primaryjoin='ErrorMispAttribute.event_id==Event.identifier')
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'))
  message = Column('message', UnicodeText)
  orig_uuid = Column('orig_uuid', Unicode(45))

  def validate(self):
    return True
