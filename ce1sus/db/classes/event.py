# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint, Table
from sqlalchemy.types import Unicode, Integer, UnicodeText, BigInteger, DateTime

from ce1sus.common.checks import is_object_viewable, is_event_owner
from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Status, Risk, Analysis, TLP, Properties, Marking
from ce1sus.db.classes.group import EventPermissions
from ce1sus.db.classes.indicator import Indicator
from ce1sus.db.classes.observables import Observable
from ce1sus.db.classes.ttp import TTPs
from ce1sus.db.common.session import Base
from ce1sus.helpers.common.converters import ValueConverter


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_EVENT_HANDLING = Table('rel_event_handling', Base.metadata,
                            Column('eih_id', BigInteger, primary_key=True, nullable=False, index=True),
                            Column('event_id', BigInteger, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True),
                            Column('marking_id', BigInteger, ForeignKey('markings.marking_id', ondelete='cascade', onupdate='cascade'), primary_key=True, index=True)
                            )


class EventGroupPermission(ExtendedLogingInformations, Base):
  event_id = Column('event_id', BigInteger, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
  group_id = Column('group_id', BigInteger, ForeignKey('groups.group_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False, index=True)
  __bit_code = None
  group = relationship('Group', primaryjoin='EventGroupPermission.group_id==Group.identifier')
  UniqueConstraint('event_id', 'group_id')

  @property
  def permissions(self):
    if self.dbcode:
      self.__bit_code = EventPermissions(self.dbcode, self)
    else:
      self.__bit_code = EventPermissions('0', self)
    return self.__bit_code

  @permissions.setter
  def permissions(self, value):
    self.__bit_code = value
    self.dbcode = value.bit_code
    self.__bit_code.parent = self

  def validate(self):
    # TODO: validate
    return True

  def to_dict(self, complete=True, inflated=False):
    return {'identifier': self.convert_value(self.uuid),
            'permissions': self.permissions.to_dict(),
            'group': self.group.to_dict(complete, inflated)}

  def populate(self, json):
    self.uuid = json.get('uuid', None)
    self.permissions.populate(json.get('permissions', None))


class Event(ExtendedLogingInformations, Base):
  title = Column('title', Unicode(255, collation='utf8_unicode_ci'), index=True, nullable=False)
  description = Column('description', UnicodeText(collation='utf8_unicode_ci'))
  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)
  status_id = Column('status_id', Integer, default=0, nullable=False)
  risk_id = Column('risk_id', Integer, nullable=False, default=0)
  analysis_id = Column('analysis_id', Integer, nullable=False, default=0)
  comments = relationship('Comment')
  last_seen = Column(DateTime, default=datetime.utcnow(), nullable=False)
  first_seen = Column(DateTime, default=datetime.utcnow(), nullable=False)
  handling = relationship(Marking, secondary='rel_event_handling')

  # TODO: Add administration of minimal objects -> checked before publishing

  groups = relationship('EventGroupPermission')
  # observables = relationship(Observable, primaryjoin='Observable.event_id==Event.identifier', lazy='dynamic')
  observables = relationship(Observable, primaryjoin='Observable.event_id==Event.identifier')
  indicators = relationship(Indicator)
  __tlp_obj = None
  dbcode = Column('code', Integer, nullable=False, default=0)
  __bit_code = None
  last_publish_date = Column('last_publish_date', DateTime)
  reports = relationship('Report')
  ttps = relationship(TTPs, uselist=False)

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

  @properties.setter
  def properties(self, bitvalue):
    """
    Property for the bit_value
    """
    self.__bit_code = bitvalue
    self.dbcode = bitvalue.bit_code

  @property
  def status(self):
    """
    returns the status

    :returns: String
    """
    return Status.get_by_id(self.status_id)

  @status.setter
  def status(self, status_text):
    """
    returns the status

    :returns: String
    """
    self.status_id = Status.get_by_value(status_text)

  @property
  def risk(self):
    """
    returns the status

    :returns: String
    """
    return Risk.get_by_id(self.risk_id)

  @risk.setter
  def risk(self, risk_text):
    """
    returns the status

    :returns: String
    """
    self.risk_id = Risk.get_by_value(risk_text)

  @property
  def analysis(self):
    """
    returns the status

    :returns: String
    """
    return Analysis.get_by_id(self.analysis_id)

  @analysis.setter
  def analysis(self, text):
    """
    returns the status

    :returns: String
    """
    self.analysis_id = Analysis.get_by_value(text)

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

  def validate(self):
    # TODO validation of an event
    return True

  def get_indicators_for_permissions(self, event_permissions, user):
    rel_objs = list()
    # TODO take into account owner
    for rel_obj in self.indicators:
      if is_object_viewable(rel_obj, event_permissions, user):
        rel_objs.append(rel_obj)
      else:
        if rel_obj.originating_group_id == user.group_id:
          rel_objs.append(rel_obj)
    return rel_objs

  def get_observables_for_permissions(self, event_permissions, user):
    rel_objs = list()
    # TODO take into account owner
    for rel_obj in self.observables:
      if is_object_viewable(rel_obj, event_permissions, user):
        rel_objs.append(rel_obj)
      else:
        if rel_obj.originating_group_id == user.group_id:
          rel_objs.append(rel_obj)
    return rel_objs

  def get_reports_for_permissions(self, event_permissions, user):
    rel_objs = list()
    # TODO take into account owner
    for rel_obj in self.reports:
      if is_object_viewable(rel_obj, event_permissions, user):
        rel_objs.append(rel_obj)
      else:
        if rel_obj.originating_group_id == user.group_id:
          rel_objs.append(rel_obj)
    return rel_objs


  def observables_count_for_permissions(self, event_permissions, user):
    return len(self.get_observables_for_permissions(event_permissions, user))


  def reports_count_for_permissions(self, event_permissions, user):
    return len(self.get_reports_for_permissions(event_permissions, user))


  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    if inflated:
      observables = list()
      for observable in self.get_observables_for_permissions(event_permissions, user):
        observables.append(observable.to_dict(complete, inflated, event_permissions, user))

      observables_count = len(observables)

      indicators = list()
      for indicator in self.get_indicators_for_permissions(event_permissions, user):
        indicators.append(indicator.to_dict(complete, inflated, event_permissions, user))

      indicators_count = len(indicators)

      reports = list()
      for report in self.get_reports_for_permissions(event_permissions, user):
        reports.append(report.to_dict(complete, inflated, event_permissions, user))

      reports_count = len(reports)

    else:
      observables = None
      # observables_count = self.observables_count_for_permissions(event_permissions)
      observables_count = -1
      reports = None
      # reports_count = self.reports_count_for_permissions(event_permissions)
      reports_count = -1
      indicators = None
      indicators_count = -1

    if complete:
      comments = list()
      if is_event_owner(self, user):
        for comment in self.comments:
          comments.append(comment.to_dict())
      groups = list()
      for group in self.groups:
        groups.append(group.to_dict(complete, False))

      result = {'identifier': self.convert_value(self.uuid),
                'int_id': self.convert_value(self.identifier),
                'title': self.convert_value(self.title),
                'description': self.convert_value(self.description),
                'last_publish_date': self.convert_value(self.last_publish_date),
                'risk': self.convert_value(self.risk),
                'status': self.convert_value(self.status),
                'tlp': self.convert_value(self.tlp),
                'analysis': self.convert_value(self.analysis),
                'creator_group': self.creator_group.to_dict(complete, False),
                'modifier_group': self.modifier.group.to_dict(complete, False),
                'originating_group': self.originating_group.to_dict(complete, False),
                'created_at': self.convert_value(self.created_at),
                'published': self.convert_value(self.properties.is_shareable),
                'modified_on': self.convert_value(self.modified_on),
                'reports': reports,
                'reports_count': reports_count,
                'first_seen': self.convert_value(None),
                'last_seen': self.convert_value(None),
                'observables': observables,
                'observables_count': observables_count,
                'indicators': indicators,
                'indicators_count': indicators_count,
                'comments': comments,
                'properties': self.properties.to_dict(),
                'groups': groups,
                'last_seen': self.convert_value(self.last_seen),
                'first_seen': self.convert_value(self.first_seen)
                }
    else:
      result = {'identifier': self.convert_value(self.uuid),
                'int_id': self.convert_value(self.identifier),
                'title': self.convert_value(self.title),
                'created_at': self.convert_value(self.created_at),
                'published': self.convert_value(self.properties.is_shareable),
                'modified_on': self.convert_value(self.modified_on),
                'observables': observables,
                'observables_count': observables_count,
                'indicators': indicators,
                'indicators_count': indicators_count,
                'reports': reports,
                'reports_count': reports_count,
                'risk': self.convert_value(self.risk),
                'status': self.convert_value(self.status),
                'tlp': self.convert_value(self.tlp),
                'analysis': self.convert_value(self.analysis),
                'creator_group': self.creator_group.to_dict(complete, False),
                'modifier_group': self.modifier.group.to_dict(complete, False),
                'originating_group': self.originating_group.to_dict(complete, False),
                'last_seen': self.convert_value(self.last_seen),
                'first_seen': self.convert_value(self.first_seen),
                'comments': None,
                'properties': self.properties.to_dict()
                }
    return result

  def populate(self, json, rest_insert=True):

    self.title = json.get('title', None)
    self.description = json.get('description', None)
    self.risk = json.get('risk', 'Undefined').title()
    self.status = json.get('status', 'Draft').title()
    self.tlp = json.get('tlp', 'Amber').title()
    self.analysis = json.get('analysis', 'Unknown').title()
    self.properties.populate(json.get('properties', None))
    self.properties.is_rest_instert = rest_insert
    self.properties.is_web_insert = not rest_insert
    # assemple first and last seen
    first_seen = json.get('first_seen', None)
    if first_seen:
      first_seen = ValueConverter.set_date(first_seen)
    else:
      first_seen = datetime.utcnow()
    self.first_seen = first_seen
    last_seen = json.get('last_seen', None)
    if last_seen:
      last_seen = ValueConverter.set_date(last_seen)
    else:
      last_seen = datetime.utcnow()
    last_publish_date = json.get('last_publish_date', None)
    if last_publish_date:
      last_publish_date = ValueConverter.set_date(last_publish_date)
    self.last_seen = last_seen
    self.properties.is_rest_instert = rest_insert
    self.properties.is_web_insert = not rest_insert

class Comment(ExtendedLogingInformations, Base):
  event_id = Column(BigInteger, ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  event = relationship('Event')
  comment = Column('comment', UnicodeText(collation='utf8_unicode_ci'), nullable=False)

  def to_dict(self, complete=True, inflated=False):
    if complete:
      result = {'identifier': self.convert_value(self.uuid),
                'comment': self.convert_value(self.comment),
                'creator_group': self.creator_group.to_dict(complete, False),
                'created_at': self.convert_value(self.created_at),
                'modified_on': self.convert_value(self.modified_on),
                'modifier_group': self.convert_value(self.modifier.group.to_dict(complete, False)),
                }
    else:
      result = {'identifier': self.convert_value(self.uuid),
                'comment': self.convert_value(self.comment),
                }
    return result

  def populate(self, json, rest_insert=True):
    self.comment = json.get('comment', None)

  def validate(self):
    # TODO: Validation of comments
    return True
