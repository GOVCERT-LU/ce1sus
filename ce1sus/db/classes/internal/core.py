# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""




from datetime import datetime
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import  DateTime, Integer

from ce1sus.common import merge_dictionaries
from ce1sus.common.checks import is_user_priviledged
from ce1sus.db.classes.internal.common import TLP, Properties
from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType
from ce1sus.db.classes.internal.usrmgt.user import User


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class SimpleLogingInformations(BaseObject):

  created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
  modified_on = Column(DateTime, default=datetime.utcnow(), nullable=False)
  # TODO: remove validation errors

  @declared_attr
  def creator_id(self):
    return Column('creator_id', BigIntegerType, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator(self):
    return relationship(User, primaryjoin='{0}.creator_id==User.identifier'.format(self.get_classname()))

  @declared_attr
  def modifier_id(self):
    return Column('modifier_id', BigIntegerType, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def modifier(self):
    return relationship(User, primaryjoin='{0}.modifier_id==User.identifier'.format(self.get_classname()))

  def to_dict(self, cache_object):
    if is_user_priviledged(cache_object.user):
      result = {'creator_id': self.convert_value(self.creator.uuid),
                 'creator': self.creator.to_dict(cache_object),
                 'modifier_id': self.convert_value(self.modifier.uuid),
                 'modifier': self.modifier.to_dict(cache_object),
                 'created_at': self.convert_value(self.created_at),
                 'modified_on': self.convert_value(self.modified_on),
                }
    else:
      pass
    result = {
              'created_at': self.convert_value(self.created_at),
              'modified_on': self.convert_value(self.modified_on)
              }
    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(parent_dict, result)


class ExtendedLogingInformations(SimpleLogingInformations):

  @declared_attr
  def creator_group_id(self):
    return Column('creator_group_id', BigIntegerType, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator_group(self):
    return relationship('Group', primaryjoin='{0}.creator_group_id==Group.identifier'.format(self.get_classname()))

  def to_dict(self, cache_object):
    parent_dict = SimpleLogingInformations.to_dict(self, cache_object)
    if is_user_priviledged(cache_object.user):
      child_dict = {'creator_group_id': self.convert_value(self.creator_group.uuid),
                    'creator_group': self.creator_group.to_dict(cache_object),
                    }
    else:
      pass
    child_dict = {}
    
    return merge_dictionaries(parent_dict, child_dict)


class BaseElement(ExtendedLogingInformations):

  tlp_level_id = Column('tlp_level_id', Integer, default=3, nullable=False)
  dbcode = Column('code', Integer, nullable=False, default=0, index=True)
  __bit_code = None
  __tlp_obj = None

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
    
  def to_dict(self, cache_object):
    result = {'tlp': self.convert_value(self.tlp),
              'properties': self.properties.to_dict(),
              }
    parent_dict = ExtendedLogingInformations.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
