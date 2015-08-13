# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 12, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey

from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.cstix.indicator.indicator import Indicator
from ce1sus.db.classes.internal.core import BaseObject, BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class ErrorBase(BaseObject, Base):

  event = relationship('Event', uselist=False)
  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  type = Column(UnicodeType(20), nullable=False)
  message = Column(UnicodeTextType, nullable=False)
  dump = Column(UnicodeTextType, nullable=False)

  __mapper_args__ = {
      'polymorphic_on': type,
      'polymorphic_identity': 'errorbase',
      'with_polymorphic':'*'
  }


class ErrorObservable(ErrorBase, Base):

  indicator_id = Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  indicator = relationship(Indicator, uselist=False)

  __mapper_args__ = {'polymorphic_identity':'errorobservable'}


class ErrorObject(ErrorBase, Base):

  observable_id = Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  observable = relationship(Observable, uselist=False)

  __mapper_args__ = {'polymorphic_identity':'errorobject'}


class ErrorAttribute(ErrorBase, Base):

  object_id = Column('object_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  object = relationship(Object, uselist=False)

  __mapper_args__ = {'polymorphic_identity':'errorattribute'}
