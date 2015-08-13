# -*- coding: utf-8 -*-

"""
(Description)

Created on Jul 3, 2015
"""




from datetime import datetime
from sqlalchemy.dialects import postgresql, mysql, sqlite
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import  DateTime, Integer, Unicode, BigInteger, UnicodeText
import uuid

from ce1sus.common import convert_value, merge_dictionaries
from ce1sus.common.checks import is_object_viewable, is_user_priviledged
from ce1sus.db.classes.internal.common import TLP, Properties


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

BigIntegerType = BigInteger()
BigIntegerType = BigIntegerType.with_variant(postgresql.BIGINT(), 'postgresql')
BigIntegerType = BigIntegerType.with_variant(mysql.BIGINT(), 'mysql')
BigIntegerType = BigIntegerType.with_variant(sqlite.INTEGER(), 'sqlite')

class UnicodeType(Unicode):

  def __init__(self, length=None, **kwargs):
    super(Unicode, self).__init__(length, **kwargs)
    self = self.with_variant(postgresql.VARCHAR(collation='utf8_unicode_ci'), 'postgresql')
    self = self.with_variant(mysql.VARCHAR(collation='utf8_unicode_ci'), 'mysql')
    self = self.with_variant(sqlite.VARCHAR(), 'sqlite')

class UnicodeTextType(UnicodeText):

  def __init__(self, length=None, **kwargs):
    super(UnicodeText, self).__init__(length, **kwargs)
    self = self.with_variant(postgresql.TEXT(collation='utf8_unicode_ci'), 'postgresql')
    self = self.with_variant(mysql.TEXT(collation='utf8_unicode_ci'), 'mysql')
    self = self.with_variant(sqlite.TEXT(), 'sqlite')


class BaseObject(object):

  @classmethod
  def get_classname(cls):
    return cls.__name__

  @declared_attr
  def identifier(self):
    return Column(u'{0}_id'.format(self.get_classname().lower()),
                  BigIntegerType,
                  primary_key=True,
                  autoincrement=True,
                  nullable=False,
                  index=True,
                  unique=True)

  @declared_attr
  def uuid(self):
    return Column('uuid',
                  UnicodeType(45),
                  default=u'{0}'.format(uuid.uuid4()),
                  nullable=False,
                  index=True,
                  unique=True)

  def to_dict(self, cache_object):
    return {'identifier': self.convert_value(self.uuid)}

  def attribute_to_dict(self, attribute, cache_object):
    if attribute:
      # TODO: Check attribute type
      if is_object_viewable(attribute, cache_object):
        return attribute.to_dict(cache_object)

  def attributelist_to_dict(self, attribute, cache_object):
    result = list()
    if attribute:
      if cache_object.inflated:
        for item in attribute:
          if is_object_viewable(item, cache_object):
            result.append(self.attribute_to_dict(item, cache_object))
    return result


class SimpleLogingInformations(BaseObject):

  created_at = Column(DateTime, default=datetime.utcnow(), nullable=False)
  modified_on = Column(DateTime, default=datetime.utcnow(), nullable=False)
  # TODO: remove validation errors

  @declared_attr
  def creator_id(self):
    return Column('creator_id', BigIntegerType, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def creator(self):
    return relationship('User', primaryjoin='{0}.creator_id==User.identifier'.format(self.get_classname()))

  @declared_attr
  def modifier_id(self):
    return Column('modifier_id', BigIntegerType, ForeignKey('users.user_id', onupdate='restrict', ondelete='restrict'), nullable=False, index=True)

  @declared_attr
  def modifier(self):
    return relationship('User', primaryjoin='{0}.modifier_id==User.identifier'.format(self.get_classname()))

  @staticmethod
  def convert_value(value):
    return convert_value(value)

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
