# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, Integer, UnicodeText

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Status, Risk, Analysis, TLP, Properties
from ce1sus.db.classes.group import EventPermissions
from ce1sus.db.classes.indicator import Indicator
from ce1sus.db.classes.observables import Observable
from ce1sus.db.common.broker import DateTime
from ce1sus.db.common.session import Base


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

  @property
  def permissions(self):
    if self.__default_bit_code is None:
      if self.default_dbcode is None:
        self.__default_bit_code = EventPermissions('0', self)
      else:
        self.__bit_code = EventPermissions(self.default_dbcode, self)
    return self.__default_bit_code

  @permissions.setter
  def permissions(self, value):
    self.__bit_code = value
    self.dbcode = value.bit_code
    self.__bit_code.parent = self


class Event(ExtendedLogingInformations, Base):
  title = Column('title', Unicode(45), index=True, unique=True, nullable=False)
  description = Column('description', UnicodeText)
  tlp_level_id = Column('tlp_level_id', Integer(1), default=3, nullable=False)
  status_id = Column('status_id', Integer(1), default=0, nullable=False)
  risk_id = Column('risk_id', Integer(1), nullable=False, default=0)
  analysis_id = Column('analysis_id', Integer(1), nullable=False, default=0)
  comments = relationship('Comment')

  # TODO: Add administration of minimal objects -> checked before publishing

  groups = relationship('EventGroupPermission')
  observables = relationship(Observable)
  indicators = relationship(Indicator)
  __tlp_obj = None
  dbcode = Column('code', Integer)
  __bit_code = None
  last_publish_date = Column('last_publish_date', DateTime)

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

  def to_dict(self, complete=True, inflated=False):
    if inflated:
      observables = list()
      for observable in self.observables:
        observables.append(observable.to_dict(complete, inflated))
    else:
      observables = None
    if complete:
      comments = list()
      for comment in self.comments:
        comments.append(comment.to_dict())

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
                'observables_count': len(self.observables),
                'comments': comments
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
                'observables_count': len(self.observables),
                'risk': self.convert_value(self.risk),
                'status': self.convert_value(self.status),
                'tlp': self.convert_value(self.tlp),
                'analysis': self.convert_value(self.analysis),
                'creator_group': self.creator_group.to_dict(complete, inflated)
                }
    return result

  def populate(self, json):

    self.title = json.get('title', None)
    self.description = json.get('description', None)
    self.risk = json.get('risk', 'Undefined').title()
    self.status = json.get('status', 'Draft').title()
    self.tlp = json.get('tlp', 'Amber').title()
    self.analysis = json.get('analysis', 'Unknown').title()
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
