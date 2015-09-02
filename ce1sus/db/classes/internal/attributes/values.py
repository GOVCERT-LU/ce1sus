# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 17, 2014
"""
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Numeric, Date, DateTime

from ce1sus.db.classes.internal.corebase import BaseObject, BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# TODO: recheck validation of values
class ValueBase(BaseObject, Base):



  type = Column(UnicodeType(20), nullable=False)
  # only one attribute value can be in
  attribute_id = Column('attribute_id', BigIntegerType, ForeignKey('attributes.attribute_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True, unique=True)

  attribute = relationship('Attribute', uselist=False, lazy='joined')

  event_id = Column('event_id', BigIntegerType, ForeignKey('events.event_id', onupdate='cascade', ondelete='cascade'), nullable=False, index=True)

  event = relationship(Event, uselist=False, lazy='joined')

  value_type_id = Column('attributetype_id', BigIntegerType, ForeignKey('attributetypes.attributetype_id'), nullable=False, index=True)

  value_type = relationship('AttributeType', uselist=False, lazy='joined')

  __mapper_args__ = {
      'polymorphic_on': type,
      'polymorphic_identity': 'valuebases',
      'with_polymorphic':'*'
  }

# pylint: disable=R0903,W0232
class StringValue(ValueBase, Base):
  """This is a container class for the STRINGVALUES table."""

  __mapper_args__ = {'polymorphic_identity':'stringvalue'}
  identifier = Column(BigIntegerType, ForeignKey('valuebases.valuebase_id', ondelete='cascade', onupdate='cascade'), primary_key=True)

  value = Column('value', UnicodeType(255), nullable=False, index=True)

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
  value = Column('value', Date, nullable=False, index=True)
  __mapper_args__ = {'polymorphic_identity':'datevalue'}
  identifier = Column(BigIntegerType, ForeignKey('valuebases.valuebase_id', ondelete='cascade', onupdate='cascade'), primary_key=True)


  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return True


# pylint: disable=R0903
class TimeStampValue(ValueBase, Base):
  """This is a container class for the DATEVALES table."""
  value = Column('value', DateTime, nullable=False, index=True)
  __mapper_args__ = {'polymorphic_identity':'timestampvalue'}
  identifier = Column(BigIntegerType, ForeignKey('valuebases.valuebase_id', ondelete='cascade', onupdate='cascade'), primary_key=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDateTime(self, 'value')


# pylint: disable=R0903
class TextValue(ValueBase, Base):
  """This is a container class for the TEXTVALUES table."""
  __mapper_args__ = {'polymorphic_identity':'textvalue'}
  identifier = Column(BigIntegerType, ForeignKey('valuebases.valuebase_id', ondelete='cascade', onupdate='cascade'), primary_key=True)

  value = Column('value', UnicodeTextType(), nullable=False)

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
  __mapper_args__ = {'polymorphic_identity':'numbervalue'}
  identifier = Column(BigIntegerType, ForeignKey('valuebases.valuebase_id', ondelete='cascade', onupdate='cascade'), primary_key=True)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDigits(self, 'value')

VALUE_TABLES = [StringValue, TextValue, NumberValue, DateValue, TimeStampValue]
