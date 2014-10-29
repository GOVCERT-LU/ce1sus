# -*- coding: utf-8 -*-

'''
(Description)

Created on Oct 16, 2014
'''
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey, Column
from sqlalchemy.sql.expression import func
from sqlalchemy.types import BIGINT

from ce1sus.db.common.broker import DateTime


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SimpleLogingInformations(object):

  created_at = Column(DateTime, default=func.now(), nullable=False)
  modified_on = Column(DateTime, default=func.now(), nullable=False)

  @declared_attr
  def creator_id(cls):
    return Column('creator_id', BIGINT, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator(cls):
    return relationship('User', primaryjoin='{0}.creator_id==User.identifier'.format(cls.__name__))

  @declared_attr
  def modifier_id(cls):
    return Column('modifier_id', BIGINT, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def modifier(cls):
    return relationship('User', primaryjoin='{0}.modifier_id==User.identifier'.format(cls.__name__))


class ExtendedLogingInformations(SimpleLogingInformations):
  @declared_attr
  def creator_group_id(cls):
    return Column('creator_group_id', BIGINT, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator_group(cls):
    return relationship('Group', primaryjoin='{0}.creator_group_id==Group.identifier'.format(cls.__name__))

