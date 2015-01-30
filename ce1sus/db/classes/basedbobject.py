# -*- coding: utf-8 -*-

'''
(Description)

Created on Oct 16, 2014
'''
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, Column
from sqlalchemy.types import Unicode

from ce1sus.db.common.broker import DateTime
from ce1sus.helpers.common.datumzait import DatumZait


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SimpleLogingInformations(object):

  created_at = Column(DateTime, default=DatumZait.utcnow(), nullable=False)
  modified_on = Column(DateTime, default=DatumZait.utcnow(), nullable=False)
  # TODO: remove validation errors

  @declared_attr
  def creator_id(cls):
    return Column('creator_id', Unicode(45), ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator(cls):
    return relationship('User', primaryjoin='{0}.creator_id==User.identifier'.format(cls.__name__), lazy='joined')

  @declared_attr
  def modifier_id(cls):
    return Column('modifier_id', Unicode(45), ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def modifier(cls):
    return relationship('User', primaryjoin='{0}.modifier_id==User.identifier'.format(cls.__name__), lazy='joined')


class ExtendedLogingInformations(SimpleLogingInformations):

  @declared_attr
  def creator_group_id(cls):
    return Column('creator_group_id', Unicode(45), ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator_group(cls):
    return relationship('Group', primaryjoin='{0}.creator_group_id==Group.identifier'.format(cls.__name__), lazy='joined')

  @declared_attr
  def originating_group_id(cls):
    return Column('originating_group_id', Unicode(45), ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def originating_group(cls):
    return relationship('Group', primaryjoin='{0}.originating_group_id==Group.identifier'.format(cls.__name__), lazy='joined')
