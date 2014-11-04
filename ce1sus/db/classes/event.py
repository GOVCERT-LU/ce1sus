# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, Table, ForeignKey
from sqlalchemy.types import Unicode, Integer, Text, Boolean

from ce1sus.db.classes.basedbobject import ExtendedLogingInformations
from ce1sus.db.classes.common import Status, Risk, Analysis, TLP, Properties
from ce1sus.db.classes.group import Group, EventPermissions
from ce1sus.db.common.broker import DateTime
from ce1sus.db.common.session import Base
from ce1sus.helpers.bitdecoder import BitBase


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventGroupPermission(ExtendedLogingInformations, Base):
  event_id = Column('event_id', Unicode(40), ForeignKey('events.event_id'), nullable=False, index=True)
  group_id = Column('group_id', Unicode(40), ForeignKey('groups.group_id'), nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False)
  __bit_code = None
  group = relationship('Group', primaryjoin='EventGroupPermission.group_id==Group.identifier')

  @property
  def permission_object(self):
    if self.__default_bit_code is None:
      if self.default_dbcode is None:
        self.__default_bit_code = EventPermissions('0', self)
      else:
        self.__bit_code = EventPermissions(self.default_dbcode, self)
    return self.__default_bit_code


class Event(ExtendedLogingInformations, Base):
  title = Column('title', Unicode(45), index=True, unique=True, nullable=False)
  description = Column('description', Text)
  tlp_level_id = Column('tlp_level_id', Boolean, default=3, nullable=False)
  status_id = Column('status_id', Boolean, default=0, nullable=False)
  risk_id = Column('risk_id', Boolean, nullable=False, default=0)
  analysis_id = Column('analysis_id', Boolean, nullable=False, default=0)

  # TODO: Add administration of minimal objects -> checked before publishing

  group_premissions = relationship('EventGroupPermission')
  objects = relationship('Object',
                         primaryjoin='and_(Event.identifier==Object.event_id, Object.parent_id==None)')
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
  def set_status(self, status_text):
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
    return Analysis.get_by_id(self.analysis_status_id)

  @analysis.setter
  def analysis(self, text):
    """
    returns the status

    :returns: String
    """
    self.analysis_status_id = Analysis.get_by_value(text)

  @property
  def tlp(self):
    """
      returns the tlp level

      :returns: String
    """
    if self.__tlp_obj is None:
      self.__tlp_obj = TLP(self.tlp_level_id)
    return self.__tlp_obj

  @tlp.setter
  def tlp(self, text):
    """
    returns the status

    :returns: String
    """
    self.__tlp_obj = None
    self.analysis_status_id = TLP.get_by_value(text)
