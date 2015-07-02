# -*- coding: utf-8 -*-

'''
(Description)

Created on Oct 16, 2014
'''
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, Column
from sqlalchemy.types import BigInteger, DateTime


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SimpleLogingInformations(object):

  created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
  modified_on = Column(DateTime, default=datetime.utcnow(), nullable=False)
  # TODO: remove validation errors

  @declared_attr
  def creator_id(cls):
    return Column('creator_id', BigInteger, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator(cls):
    return relationship('User', primaryjoin='{0}.creator_id==User.identifier'.format(cls.__name__))

  @declared_attr
  def modifier_id(cls):
    return Column('modifier_id', BigInteger, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def modifier(cls):
    return relationship('User', primaryjoin='{0}.modifier_id==User.identifier'.format(cls.__name__))

  @property
  def timestamp(self):
    return self.modified_on

  @property
  def information_source(self):
    return self.creator_group

  @information_source.setter
  def information_source(self, value):
    self.creator_group = value

class ExtendedLogingInformations(SimpleLogingInformations):

  @declared_attr
  def creator_group_id(cls):
    return Column('creator_group_id', BigInteger, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator_group(cls):
    return relationship('Group', primaryjoin='{0}.creator_group_id==Group.identifier'.format(cls.__name__))

  @declared_attr
  def originating_group_id(cls):
    return Column('originating_group_id', BigInteger, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def originating_group(cls):
    return relationship('Group', primaryjoin='{0}.originating_group_id==Group.identifier'.format(cls.__name__))

  @declared_attr
  def owner_group_id(cls):
    return Column('owner_group_id', BigInteger, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def owner_group(cls):
    return relationship('Group', primaryjoin='{0}.owner_group_id==Group.identifier'.format(cls.__name__))

  # Indicator properties
  # producer = owner_group
  @property
  def producer(self):
    return self.owner_group

  @producer.setter
  def producer(self, value):
    self.owner_group = value
