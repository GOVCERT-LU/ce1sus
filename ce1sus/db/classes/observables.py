# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 11, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Unicode, UnicodeText, Integer, BigInteger

from ce1sus.common.checks import is_object_viewable
from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Properties, TLP
from ce1sus.db.classes.object import Object
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableKeyword(Base):
  observable_id = Column('observable_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False)
  keyword = Column('keyword', Unicode(255), nullable=False, index=True)


_REL_OBSERVABLE_COMPOSITION = Table('rel_observable_composition', Base.metadata,
                                    Column('roc_id', BigInteger, primary_key=True, nullable=False, index=True),
                                    Column('observablecomposition_id', BigInteger, ForeignKey('observablecompositions.observablecomposition_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                                    Column('child_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
                                    )


class ObservableComposition(Base):
  parent_id = Column('parent_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  parent = relationship('Observable')
  operator = Column('operator', Unicode(3), default=u'OR')
  # observables = relationship('Observable', secondary='rel_observable_composition', lazy='dynamic')
  observables = relationship('Observable', secondary='rel_observable_composition', lazy='joined', backref='composed_parent')
  dbcode = Column('code', Integer, nullable=False, default=0, index=True)
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

  def validate(self):
    return True

  def get_observables_for_permissions(self, event_permissions, user):
    rel_objs = list()
    for rel_obj in self.observables:
      if is_object_viewable(rel_obj, event_permissions, user):
        rel_objs.append(rel_obj)
    return rel_objs
    """
    if event_permissions:
      if event_permissions.can_validate:
        return self.observables.all()
      else:
        # count validated ones
        return self.observables.filter(Observable.dbcode.op('&')(1) == 1).all()
    else:
      # count shared and validated
      return self.observables.filter(Observable.dbcode.op('&')(3) == 3).all()
    """

  def observables_count_for_permissions(self, event_permissions):
    return len(self.get_observables_for_permissions(event_permissions))
    """
    if event_permissions:
      if event_permissions.can_validate:
        return self.observables.count()
      else:
        # count validated ones
        return self.observables.filter(Observable.dbcode.op('&')(1) == 1).count()
    else:
      # count shared and validated
      return self.observables.filter(Observable.dbcode.op('&')(3) == 3).count()
    """
  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    observables = list()
    for observable in self.get_observables_for_permissions(event_permissions, user):
      observables.append(observable.to_dict(complete, inflated, event_permissions, user))

    if observables:
      observables_count = len(observables)
    else:
      # observables_count = self.observables_count_for_permissions(event_permissions)
      observables_count = -1

    return {'identifier': self.convert_value(self.uuid),
            'operator': self.convert_value(self.operator),
            'observables': observables,
            'observables_count': observables_count,
            'properties': self.properties.to_dict()
            }

  def populate(self, json, rest_insert=True):
    self.operator = json.get('operator', None)
    self.properties.populate(json.get('properties', None))


class RelatedObservable(ExtendedLogingInformations, Base):
  parent_id = Column('parent_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  parent = relationship('Observable', primaryjoin='RelatedObservable.parent_id==Observable.identifier', uselist=False)
  child_id = Column('child_id', BigInteger, ForeignKey('observables.observable_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)
  relation = Column('relation', BigInteger)
  confidence = Column('confidence', Integer)
  observable = relationship('Observable', primaryjoin='RelatedObservable.child_id==Observable.identifier', uselist=False)

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    # flatten related object
    observable = self.observable.to_dict(complete, inflated, event_permissions, user)
    observable['relation'] = self.convert_value(self.relation)
    observable['confidence'] = self.convert_value(self.confidence)
    observable['parent_observable_id'] = self.convert_value(self.parent_id)
    return {'identifier': self.convert_value(self.uuid),
            'observable': observable,
            'relation': self.convert_value(self.relation),
            'confidence': self.convert_value(self.confidence),
            'parent_id': self.convert_value(self.parent_id),
            }

  def validate(self):
    # TODO: validate
    return True


class Observable(ExtendedLogingInformations, Base):

  title = Column('title', Unicode(255), index=True)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  object = relationship(Object, back_populates='parent', uselist=False, primaryjoin='Object.parent_id==Observable.identifier', lazy='joined')
  observable_composition = relationship('ObservableComposition', uselist=False, lazy='joined')
  keywords = relationship('ObservableKeyword', backref='observable')
  event = relationship('Event', uselist=False, primaryjoin='Observable.event_id==Event.identifier')
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True)
  version = Column('version', Unicode(40), default=u'1.0.0', nullable=False)
  dbcode = Column('code', Integer, nullable=False, default=0, index=True)
  parent = relationship('Event', uselist=False, primaryjoin='Observable.parent_id==Event.identifier')
  parent_id = Column('parent_id', BigInteger, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), index=True)
  __bit_code = None

  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """

    return TLP.get_by_id(self.tlp_level_id)

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    self.tlp_level_id = TLP.get_by_value(text)

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

  def validate(self):
    return True

  def get_object_for_permissions(self, event_permissions, user):
    if self.object:
      if is_object_viewable(self.object, event_permissions, user):
        return self.object
    return None

  def get_composed_observable_for_permissions(self, event_permissions, user):
    if self.observable_composition:
      if user and user.group:
        if is_object_viewable(self.observable_composition, event_permissions, user):
          return self.observable_composition
    return None

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    if inflated:
      obj = self.get_object_for_permissions(event_permissions, user)
      if obj:
        obj = obj.to_dict(complete, inflated, event_permissions, user)
    else:
      obj = None

    composed = self.get_composed_observable_for_permissions(event_permissions, user)
    if composed:
      composed = composed.to_dict(complete, inflated, event_permissions, user)

    if complete:
      result = {'identifier': self.convert_value(self.uuid),
                'title': self.convert_value(self.title),
                'description': self.convert_value(self.description),
                'object': obj,
                'version': self.convert_value(self.version),
                'observable_composition': composed,
                'creator_group': self.creator_group.to_dict(complete, False),
                'created_at': self.convert_value(self.created_at),
                'modified_on': self.convert_value(self.modified_on),
                'modifier_group': self.modifier.group.to_dict(complete, False),
                'tlp': self.convert_value(self.tlp),
                'properties': self.properties.to_dict(),
                'originating_group': self.originating_group.to_dict(complete, False),
                }
    else:
      result = {'identifier': self.convert_value(self.uuid),
                'title': self.convert_value(self.title),
                'object': obj,
                'observable_composition': composed,
                'creator_group': self.creator_group.to_dict(complete, False),
                'modifier_group': self.modifier.group.to_dict(complete, False),
                'created_at': self.convert_value(self.created_at),
                'modified_on': self.convert_value(self.modified_on),
                'tlp': self.convert_value(self.tlp),
                'properties': self.properties.to_dict(),
                'originating_group': self.originating_group.to_dict(complete, False),
                }

    return result

  def populate(self, json, rest_insert=True):
    self.title = json.get('title', None)
    self.description = json.get('description', None)
    self.properties.populate(json.get('properties', None))
    # TODO: make valid for inflated
    self.properties.is_rest_instert = rest_insert
    self.properties.is_web_insert = not rest_insert
    self.tlp = json.get('tlp', 'Amber').title()
