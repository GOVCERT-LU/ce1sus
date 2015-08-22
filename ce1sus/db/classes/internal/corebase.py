# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 18, 2015
"""
from sqlalchemy.dialects import postgresql, mysql, sqlite
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.sql.schema import Column
from sqlalchemy.types import BigInteger, Unicode, UnicodeText
import uuid

from ce1sus.common import convert_value
from ce1sus.common.checks import is_object_viewable


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

  @classmethod
  def get_class(cls):
    return cls

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

  @staticmethod
  def convert_value(value):
    return convert_value(value)

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
    return None
