# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2014
"""
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Integer

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.core import BigIntegerType, UnicodeType
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_OBSERVABLE_COMPOSITION = Table('rel_observable_composition', getattr(Base, 'metadata'),
                                    Column('roc_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                    Column('observablecomposition_id', BigIntegerType, ForeignKey('observablecompositions.observablecomposition_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                    Column('child_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
                                    )

_REL_OBSERVABLE_STRUCTUREDTEXT = Table('rel_observable_structuredtext', getattr(Base, 'metadata'),
                                       Column('rtobservablest_id', BigIntegerType, primary_key=True, nullable=False, index=True),
                                       Column('observable_id',
                                              BigIntegerType,
                                              ForeignKey('observables.observable_id',
                                                         ondelete='cascade',
                                                         onupdate='cascade'),
                                              index=True,
                                              nullable=False),
                                       Column('structuredtext_id',
                                             BigIntegerType,
                                             ForeignKey('structuredtexts.structuredtext_id',
                                                        ondelete='cascade',
                                                        onupdate='cascade'),
                                              primary_key=True,
                                              index=True)
                                       )


class ObservableKeyword(Entity, Base):
  observable_id = Column('observable_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False)
  keyword = Column('keyword', UnicodeType(255), nullable=False, index=True)

  @property
  def parent(self):
    return self.observable

  def to_dict(self, cache_object):
    result = {'keyword', self.convert_value(self.keyword)}
    parent = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent)

class ObservableComposition(Entity, Base):

  operator = Column('operator', UnicodeType(3), default=u'OR')
  observables = relationship('Observable', secondary='rel_observable_composition', backref='observable_composition')

  # ce1sus specific
  observable_id = Column('parent_id', BigIntegerType, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @property
  def parent(self):
    return self.observable


  def validate(self):
    return True

  def to_dict(self, cache_object):
    observables = self.attributelist_to_dict(self.observables, cache_object)
    if observables:
      observables_count = len(observables)
    else:
      observables_count = -1

    result = {'operator': self.convert_value(self.operator),
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

  namespace = Column('namespace', UnicodeType(255), index=True, nullable=False, default=u'ce1sus')

  title = Column('title', UnicodeType(255), index=True)
  description = relationship(StructuredText, secondary=_REL_OBSERVABLE_STRUCTUREDTEXT, uselist=False, backref='observable_description')

  object = relationship(Object, uselist=False, primaryjoin='Object.parent_id==Observable.identifier', backref='observable')
  # TODO: observable event (Note: different than the event used here)
  observable_composition = relationship('ObservableComposition', uselist=False, backref='observable')
  idref = Column(u'idref', UnicodeType(255), nullable=True, index=True)
  sighting_count = Column(u'sighting_count', Integer, nullable=True, index=True)
  keywords = relationship('ObservableKeyword', backref='observable')

  @property
  def parent(self):
    if self.event:
      return self.event
    elif self.indicator:
      return self.indicator
    elif self.observable_composition:
      return self.observable_composition
    elif self.related_observable:
      return self.related_observable

  def validate(self):
    return True

  def to_dict(self, cache_object):
    if cache_object.inflated:
      obj = self.attribute_to_dict(self.object, cache_object)
      composed = self.attribute_to_dict(self.observable_composition, cache_object)
    else:
      obj = None
      composed = None

    if cache_object.complete:
      keywords = self.attributelist_to_dict(self.keywords, cache_object)

      description = self.attribute_to_dict(self.description, cache_object)

      result = {'id_': self.convert_value(self.id_),
                'idref': self.convert_value(self.idref),
                'title': self.convert_value(self.title),
                'sighting_count': self.convert_value(self.sighting_count),
                'description': description,
                'object': obj,
                'observable_composition': composed,
                'keywords': keywords
                }
    else:
      result = {'id_': self.convert_value(self.id_),
                'idref': self.convert_value(self.idref),
                'title': self.convert_value(self.title),
                'object': obj,
                'observable_composition': composed,
                }

    parent_dict = Entity.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)

