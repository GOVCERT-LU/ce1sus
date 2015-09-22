# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 12, 2015
"""
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import Column, ForeignKey

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.cstix.indicator.indicator import Indicator
from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.report import Report
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class ErrorBase(BaseObject, Base):

  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  event = relationship('Event', uselist=False)

  message = Column(UnicodeTextType, nullable=False)
  dump = Column(UnicodeTextType, nullable=False)

  type = Column(UnicodeType(20), nullable=False)

  __mapper_args__ = {
      'polymorphic_on': type,
      'polymorphic_identity': 'errorbase',
      'with_polymorphic':'*'
  }

  def to_dict(self, cache_object):
    if cache_object.permission_controller.is_instance_owner(self, cache_object):
      result = {'event_id': self.convert_value(self.event.uuid),
                'message': self.convert_value(self.message),
                'dump': self.convert_value(self.dump)
                }
      parent_dict = BaseObject.to_dict(self, cache_object)
      return merge_dictionaries(result, parent_dict)
    else:
      return dict()

class ErrorObservable(ErrorBase, Base):

  identifier = Column(BigIntegerType, ForeignKey('errorbases.errorbase_id', onupdate='cascade', ondelete='cascade'), primary_key=True)

  indicator_id = Column('indicator_id', BigIntegerType, ForeignKey('indicators.indicator_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  indicator = relationship(Indicator, uselist=False)

  __mapper_args__ = {'polymorphic_identity':'errorobservable'}

  def to_dict(self, cache_object):
    if cache_object.permission_controller.is_instance_owner(self, cache_object):
      result = {'indicator_id': self.convert_value(self.indicator.uuid)
                }
      parent_dict = ErrorBase.to_dict(self, cache_object)
      return merge_dictionaries(result, parent_dict)
    else:
      return dict()

class ErrorObject(ErrorBase, Base):

  identifier = Column(BigIntegerType, ForeignKey('errorbases.errorbase_id', onupdate='cascade', ondelete='cascade'), primary_key=True)
  observable_id = Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  observable = relationship(Observable, uselist=False)

  __mapper_args__ = {'polymorphic_identity':'errorobject'}

  def to_dict(self, cache_object):
    if cache_object.permission_controller.is_instance_owner(self, cache_object):
      result = {'observable_id': self.convert_value(self.observable.uuid)
                }
      parent_dict = ErrorBase.to_dict(self, cache_object)
      return merge_dictionaries(result, parent_dict)
    else:
      return dict()

class ErrorAttribute(ErrorBase, Base):

  identifier = Column(BigIntegerType, ForeignKey('errorbases.errorbase_id', onupdate='cascade', ondelete='cascade'), primary_key=True)

  object_id = Column('object_id', BigIntegerType, ForeignKey('objects.object_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  object = relationship(Object, uselist=False)

  __mapper_args__ = {'polymorphic_identity':'errorattribute'}

  def to_dict(self, cache_object):
    if cache_object.permission_controller.is_instance_owner(self, cache_object):
      result = {'object_id': self.convert_value(self.object.uuid)
                }
      parent_dict = ErrorBase.to_dict(self, cache_object)
      return merge_dictionaries(result, parent_dict)
    else:
      return dict()

class ErrorReference(ErrorBase, Base):

  identifier = Column(BigIntegerType, ForeignKey('errorbases.errorbase_id', onupdate='cascade', ondelete='cascade'), primary_key=True)

  report_id = Column('report_id', BigIntegerType, ForeignKey('reports.report_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  report = relationship(Report, uselist=False)

  __mapper_args__ = {'polymorphic_identity':'errorreference'}

  def to_dict(self, cache_object):
    if cache_object.permission_controller.is_instance_owner(self, cache_object):
      result = {'report_id': self.convert_value(self.report.uuid)
                }
      parent_dict = ErrorBase.to_dict(self, cache_object)
      return merge_dictionaries(result, parent_dict)
    else:
      return dict()
