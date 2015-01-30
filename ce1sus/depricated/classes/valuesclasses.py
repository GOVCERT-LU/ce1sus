# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""
from sqlalchemy import Column, Integer, String, ForeignKey

from ce1sus.db.common.broker import DateTime
from ce1sus.depricated.brokers.basefoo import BASE
from ce1sus.helpers.common.converters import ValueConverter
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=R0903,W0232
class OldStringValue(BASE):
  """This is a container class for the STRINGVALUES table."""

  __tablename__ = "StringValues"

  identifier = Column('StringValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  event_id = Column(Integer, ForeignKey('Events.event_id'))

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

  @staticmethod
  def convert(value):
    return unicode(value)


# pylint: disable=R0903
class OldDateValue(BASE):
  """This is a container class for the DATEVALES table."""

  __tablename__ = "DateValues"

  identifier = Column('DateValue_id', Integer, primary_key=True)
  value = Column('value', DateTime)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  event_id = Column(Integer, ForeignKey('Events.event_id'))

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDateTime(self, 'value')

  @staticmethod
  def convert(value):
    return ValueConverter.set_date(value)


class OldTextValue(BASE):
  """This is a container class for the TEXTVALUES table."""

  __tablename__ = "TextValues"

  identifier = Column('TextValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  event_id = Column(Integer, ForeignKey('Events.event_id'))

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

  @staticmethod
  def convert(value):
    return unicode(value)


# pylint: disable=R0903
class OldNumberValue(BASE):
  """This is a container class for the NUMBERVALUES table."""

  __tablename__ = "NumberValues"
  identifier = Column('NumberValue_id', Integer, primary_key=True)
  value = Column('value', Integer)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  event_id = Column(Integer, ForeignKey('Events.event_id'))

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDigits(self, 'value')

  @staticmethod
  def convert(value):
    return int(value)
