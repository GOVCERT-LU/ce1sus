# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2014
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.ccybox.common.measuresource import MeasureSource
from ce1sus.db.classes.ccybox.core.relations import _REL_OBSERVABLE_STRUCTUREDTEXT, _REL_OBSERVABLE_OBJECT, _REL_OBSERVABLE_COMPOSITION
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.related import RelatedObservable
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.cstix.indicator.relations import _REL_INDICATOR_OBSERVABLE
from ce1sus.db.classes.internal.corebase import BigIntegerType, UnicodeType
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.relations import _REL_EVENT_OBSERVABLE
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class ObservableKeyword(Entity, Base):
  observable_id = Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False)
  observable = relationship('Observable', uselist=False)
  keyword = Column('keyword', UnicodeType(255), nullable=False, index=True)

  _PARENTS = ['observable']

  def to_dict(self, cache_object):
    result = {'keyword', self.convert_value(self.keyword)}
    parent = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent)

class ObservableComposition(Entity, Base):

  operator = Column('operator', UnicodeType(3), default=u'OR')
  observables = relationship('Observable', secondary=_REL_OBSERVABLE_COMPOSITION, back_populates='composedobservable')

  # ce1sus specific
  observable_id = Column('parent_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  observable = relationship('Observable', uselist=False)
  _PARENTS = ['observable']

  @property
  def parent(self):
    return self.observable

  @parent.setter
  def parent(self, instance):
    self.observable = instance

  def validate(self):
    return True

  def to_dict(self, cache_object):
    instance = self.get_instance([], cache_object)

    observables = instance.attributelist_to_dict('observables', cache_object)
    if observables:
      observables_count = len(observables)
    else:
      observables_count = -1

    result = {'operator': instance.convert_value(instance.operator),
              'observables': observables,
              'observables_count': observables_count,
              }
    parent = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent)

class Observable(Entity, Base):

  @hybrid_property
  def id_(self):
    return u'{0}:{1}-{2}'.format(self.namespace, self.get_classname(), self.uuid)

  @id_.setter
  def id_(self, value):
    if value:
      self.set_id(value)

  @property
  def object_(self):
    return self.object

  @object_.setter
  def object_(self, value):
    self.object = value

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')

  title = Column('title', UnicodeType(255), index=True)
  description = relationship(StructuredText, secondary=_REL_OBSERVABLE_STRUCTUREDTEXT, uselist=False)

  object = relationship(Object, uselist=False, secondary=_REL_OBSERVABLE_OBJECT, back_populates='observable')
  # TODO: observable event (Note: different than the event used here)
  observable_composition = relationship('ObservableComposition', uselist=False, back_populates='observable')
  idref = Column(u'idref', UnicodeType(255), nullable=True, index=True)
  sighting_count = Column(u'sighting_count', Integer, nullable=True, index=True)
  keywords = relationship('ObservableKeyword')

  _PARENTS = ['event', 'indicator', 'composedobservable', 'related_observable']

  event = relationship('Event', uselist=False, secondary=_REL_EVENT_OBSERVABLE)
  related_observable = relationship(RelatedObservable, primaryjoin='RelatedObservable.child_id==Observable.identifier', uselist=False)
  indicator = relationship('Indicator', uselist=False, secondary=_REL_INDICATOR_OBSERVABLE)
  composedobservable = relationship('ObservableComposition', secondary=_REL_OBSERVABLE_COMPOSITION, uselist=False)
  observable_source = relationship(MeasureSource)
  def validate(self):
    return True

  def get_populated(self, cache_object):
    return self.get_instance([Observable.description, Observable.object, Observable.observable_composition, Observable.keywords], cache_object)

  def to_dict(self, cache_object):
    instance = self.get_populated(cache_object)

    if cache_object.inflated:
      obj = instance.attribute_to_dict(instance.object, cache_object)
      composed = instance.attribute_to_dict(instance.observable_composition, cache_object)
    else:
      obj = None
      composed = None

    if cache_object.complete:
      keywords = instance.attributelist_to_dict('keywords', cache_object)

      description = instance.attribute_to_dict(instance.description, cache_object)

      result = {'id_': instance.convert_value(instance.id_),
                'idref': instance.convert_value(instance.idref),
                'title': instance.convert_value(instance.title),
                'sighting_count': instance.convert_value(instance.sighting_count),
                'description': description,
                'object': obj,
                'observable_composition': composed,
                'keywords': keywords
                }
    else:
      result = {'id_': instance.convert_value(instance.id_),
                'idref': instance.convert_value(instance.idref),
                'title': instance.convert_value(instance.title),
                'object': obj,
                'observable_composition': composed,
                }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

