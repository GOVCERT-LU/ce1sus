# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 17, 2014
"""
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, BIGINT, Text, Numeric

from ce1sus.db.common.broker import DateTime
from ce1sus.db.common.session import Base
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ValueBase(object):

  @declared_attr
  def attribute_id(self):
    return Column('attribute_id', BIGINT, ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  @declared_attr
  def attribute(self):
    return relationship('Attribute', uselist=False)

  @declared_attr
  def event_id(self):
    return Column('event_id', BIGINT, ForeignKey('events.event_id'))

  @declared_attr
  def event(self):
    return relationship("Event", uselist=False)


# pylint: disable=R0903,W0232
class StringValue(ValueBase, Base):
  """This is a container class for the STRINGVALUES table."""

  value = Column('value', Unicode(255), nullable=False, index=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateAlNum(self,
                                         'value',
                                         minLength=1,
                                         withSpaces=True,
                                         withSymbols=True)


# pylint: disable=R0903
class DateValue(ValueBase, Base):
  """This is a container class for the DATEVALES table."""
  value = Column('value', DateTime, nullable=False, index=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDateTime(self, 'value')


# pylint: disable=R0903
class TextValue(ValueBase, Base):
  """This is a container class for the TEXTVALUES table."""
  value = Column('value', Text, nullable=False)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateAlNum(self,
                                         'value',
                                         minLength=1,
                                         withNonPrintableCharacters=True,
                                         withSpaces=True,
                                         withSymbols=True)


# pylint: disable=R0903
class NumberValue(ValueBase, Base):
  """This is a container class for the NUMBERVALUES table."""
  value = Column('value', Numeric, nullable=False, index=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDigits(self, 'value')
