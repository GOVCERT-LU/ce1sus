# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, UniqueConstraint, Table
from sqlalchemy.types import Unicode, Integer, UnicodeText, BigInteger

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Status, Risk, Analysis, TLP, Properties
from ce1sus.db.classes.group import EventPermissions
from ce1sus.db.classes.indicator import Indicator
from ce1sus.db.classes.observables import Observable
from ce1sus.db.common.broker import DateTime
from ce1sus.db.common.session import Base
from ce1sus.db.classes.report import Report


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventGroupPermission(ExtendedLogingInformations, Base):
  event_id = Column('event_id', Unicode(40), ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
  group_id = Column('group_id', Unicode(40), ForeignKey('groups.group_id', ondelete='cascade', onupdate='cascade'), nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False)
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
    return {'identifier': self.convert_value(self.identifier),
            'permissions': self.permissions.to_dict(),
            'group': self.group.to_dict(complete, inflated)}


class Event(ExtendedLogingInformations, Base):
  title = Column('title', Unicode(45), index=True, nullable=False)
  description = Column('description', UnicodeText)
  tlp_level_id = Column('tlp_level_id', Integer(1), default=3, nullable=False)
  status_id = Column('status_id', Integer(1), default=0, nullable=False)
  risk_id = Column('risk_id', Integer(1), nullable=False, default=0)
  analysis_id = Column('analysis_id', Integer(1), nullable=False, default=0)
  comments = relationship('Comment')

  # TODO: Add administration of minimal objects -> checked before publishing

  groups = relationship('EventGroupPermission')
  # observables = relationship(Observable, primaryjoin='Observable.event_id==Event.identifier', lazy='dynamic')
  observables = relationship(Observable, primaryjoin='Observable.event_id==Event.identifier')
  indicators = relationship(Indicator)
  __tlp_obj = None
  dbcode = Column('code', Integer, nullable=False, default=0)
  __bit_code = None
  last_publish_date = Column('last_publish_date', DateTime)
  reports = relationship('Report', lazy='dynamic')

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

  def get_observables_for_permissions(self, event_permissions):
    rel_objs = list()
    if event_permissions:
      if event_permissions.can_validate:
        for rel_obj in self.observables:
          if rel_obj.properties.is_shareable:
            rel_objs.append(rel_obj)
      # TODO take into account owner
    else:
      for rel_obj in self.observables:
        if rel_obj.properties.is_validated_and_shared:
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

  def get_reports_for_permissions(self, event_permissions):
    rel_objs = list()
    if event_permissions:
      if event_permissions.can_validate:
        for rel_obj in self.reports:
          if rel_obj.properties.is_shareable:
            rel_objs.append(rel_obj)
      # TODO take into account owner
    else:
      for rel_obj in self.reports:
        if rel_obj.properties.is_validated_and_shared:
          rel_objs.append(rel_obj)
    return rel_objs
    """
    if event_permissions:
      if event_permissions.can_validate:
        return self.reports.all()
      else:
        # count validated ones
        return self.reports.filter(Report.dbcode.op('&')(1) == 1).all()
    else:
      # count shared and validated
      return self.reports.filter(Report.dbcode.op('&')(3) == 3).all()
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

  def reports_count_for_permissions(self, event_permissions):
    return len(self.get_reports_for_permissions(event_permissions))
    """
    if event_permissions:
      if event_permissions.can_validate:
        return self.reports.count()
      else:
        # count validated ones
        return self.reports.filter(Report.dbcode.op('&')(1) == 1).count()
    else:
      # count shared and validated
      return self.reports.filter(Report.dbcode.op('&')(3) == 3).count()
    """

  def to_dict(self, complete=True, inflated=False, event_permissions=None, owner=False):
    if inflated:
      observables = list()
      for observable in self.get_observables_for_user(event_permissions):
        observables.append(observable.to_dict(complete, inflated, event_permissions))

      observables_count = len(observables)

      reports = list()
      for report in self.get_reports_for_user(event_permissions):
        reports.append(report.to_dict(complete, inflated, event_permissions))

      reports_count = len(reports)

    else:
      observables = None
      observables_count = self.observables_count_for_permissions(event_permissions)
      reports = None
      reports_count = self.reports_count_for_permissions(event_permissions)

    if complete:
      comments = list()
      if owner:
        for comment in self.comments:
          comments.append(comment.to_dict())
      groups = list()
      for group in self.groups:
        groups.append(group.to_dict(complete, False))

      result = {'identifier': self.convert_value(self.identifier),
                'title': self.convert_value(self.title),
                'description': self.convert_value(self.description),
                'last_publish_date': self.convert_value(self.last_publish_date),
                'risk': self.convert_value(self.risk),
                'status': self.convert_value(self.status),
                'tlp': self.convert_value(self.tlp),
                'analysis': self.convert_value(self.analysis),
                'creator_group': self.creator_group.to_dict(complete, inflated),
                'created_at': self.convert_value(self.created_at),
                'published': self.convert_value(self.properties.is_shareable),
                'modified_on': self.convert_value(self.modified_on),
                # TODO: add first and last seen
                'first_seen': self.convert_value(None),
                'last_seen': self.convert_value(None),
                'observables': observables,
                'observables_count': observables_count,
                'comments': comments,
                'properties': self.properties.to_dict(),
                'groups': groups
                }
    else:
      result = {'identifier': self.convert_value(self.identifier),
                'title': self.convert_value(self.title),
                'creator_group': self.creator_group.to_dict(False),
                'created_at': self.convert_value(self.created_at),
                'published': self.convert_value(self.properties.is_shareable),
                'modified_on': self.convert_value(self.modified_on),
                # TODO: add first and last seen
                'first_seen': self.convert_value(None),
                'last_seen': self.convert_value(None),
                'observables': observables,
                'observables_count': observables_count,
                'reports': reports,
                'reports_count': reports_count,
                'risk': self.convert_value(self.risk),
                'status': self.convert_value(self.status),
                'tlp': self.convert_value(self.tlp),
                'analysis': self.convert_value(self.analysis),
                'creator_group': self.creator_group.to_dict(complete, inflated),
                'comments': None,
                'properties': self.properties.to_dict()
                }
    return result

  def populate(self, json):

    self.title = json.get('title', None)
    self.description = json.get('description', None)
    self.risk = json.get('risk', 'Undefined').title()
    self.status = json.get('status', 'Draft').title()
    self.tlp = json.get('tlp', 'Amber').title()
    self.analysis = json.get('analysis', 'Unknown').title()
    self.properties.populate(json.get('properties', None))
    # TODO: populate properties
    # self.published = json.get('published', None)


class Comment(ExtendedLogingInformations, Base):
  event_id = Column(Unicode(40), ForeignKey('events.event_id', ondelete='cascade', onupdate='cascade'), index=True, nullable=False)
  event = relationship('Event')
  comment = Column('comment', UnicodeText, nullable=False)

  def to_dict(self, complete=True, inflated=False):
    if complete:
      result = {'identifier': self.convert_value(self.identifier),
                'comment': self.convert_value(self.comment),
                'creator_group': self.creator_group.to_dict(complete, inflated),
                'created_at': self.convert_value(self.created_at),
                'modified_on': self.convert_value(self.modified_on),
                'modifier_group': self.convert_value(self.modifier.group.to_dict(complete, inflated)),
                }
    else:
      result = {'identifier': self.convert_value(self.identifier),
                'comment': self.convert_value(self.comment),
                }
    return result

  def populate(self, json):
    self.comment = json.get('comment', None)

  def validate(self):
    # TODO: Validation of comments
    return True
