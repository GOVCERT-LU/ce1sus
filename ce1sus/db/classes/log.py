# -*- coding: utf-8 -*-

"""
(Description)

Created on Apr 7, 2015
"""

from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Boolean

from ce1sus.db.classes.internal.core import BaseObject, BigIntegerType, UnicodeTextType, UnicodeType
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ErrorMispAttribute(BaseObject, Base):

  object_id = Column('object_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'))

  value = Column('value', UnicodeTextType())
  category = Column('category', UnicodeType(255))
  type_ = Column('type', UnicodeType(255))
  observable_id = Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'))

  misp_id = Column('misp_id', UnicodeType(255))
  is_ioc = Column('is_ioc', Boolean)
  share = Column('share', Boolean)

  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'))
  message = Column('message', UnicodeTextType())
  orig_uuid = Column('orig_uuid', UnicodeType(45))

  def validate(self):
    return True
