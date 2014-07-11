# -*- coding: utf-8 -*-

"""
module containing all informations about attribute values

Created: Aug 25, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, ValidationException, \
NothingFoundException, TooManyResultsFoundException, IntegrityException, \
BrokerException
import sqlalchemy.orm.exc
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from dagr.db.session import BASE
from dagr.db.broker import DateTime
from dagr.helpers.validator.objectvalidator import ObjectValidator
from dagr.helpers.converters import ValueConverter
from ce1sus.brokers.definition.definitionclasses import AttributeDefinition
from dagr.helpers.objects import get_class


# pylint: disable=R0903,W0232
class StringValue(BASE):
  """This is a container class for the STRINGVALUES table."""

  __tablename__ = "StringValues"

  identifier = Column('StringValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute", uselist=False)
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False)

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
class DateValue(BASE):
  """This is a container class for the DATEVALES table."""

  __tablename__ = "DateValues"

  identifier = Column('DateValue_id', Integer, primary_key=True)
  value = Column('value', DateTime)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute",
                           uselist=False)
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDateTime(self, 'value')

  @staticmethod
  def convert(value):
    return ValueConverter.set_date(value)


# pylint: disable=R0903
class TextValue(BASE):
  """This is a container class for the TEXTVALUES table."""

  __tablename__ = "TextValues"

  identifier = Column('TextValue_id', Integer, primary_key=True)
  value = Column('value', String)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute",
                           uselist=False)
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False)

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
class NumberValue(BASE):
  """This is a container class for the NUMBERVALUES table."""

  __tablename__ = "NumberValues"
  identifier = Column('NumberValue_id', Integer, primary_key=True)
  value = Column('value', Integer)
  attribute_id = Column(Integer, ForeignKey('Attributes.attribute_id'))
  attribute = relationship("Attribute",
                           uselist=False)
  event_id = Column(Integer, ForeignKey('Events.event_id'))
  event = relationship("Event", uselist=False)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    return ObjectValidator.validateDigits(self, 'value')

  @staticmethod
  def convert(value):
    return int(value)


class ValueBroker(BrokerBase):
  """
  This broker is used internally to serparate the values to their
  corresponding tables

  Note: Only used by the AttributeBroker
  """
  def __init__(self, session):
    BrokerBase.__init__(self, session)
    self.__clazz = StringValue

  @property
  def clazz(self):
    """
    returns the class used for this value broker

    Note: May vary during its lifetime

    """
    return self.__clazz

  @clazz.setter
  def clazz(self, clazz):
    """
    setter for the class
    """
    self.__clazz = clazz

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return self.__clazz

  @staticmethod
  def get_class_by_attribute(attribute):
    """
    returns class for the attribute

    :param attribute: the attribute in context
    :type attribute: Class
    """
    return ValueBroker.get_class_by_attr_def(
                                                attribute.definition)

  @staticmethod
  def get_class_by_string(classname):
    """
    returns class for the attribute

    :param classname: the name of the class
    :type classname: Class
    """
    return get_class('ce1sus.brokers.valuebroker', classname)

  @staticmethod
  def get_class_by_attr_def(definition):
    """
    returns class for the attribute

    :param attribute: the attribute in context
    :type attribute: Attribute
    """
    return ValueBroker.get_class_by_string(definition.classname)

  @staticmethod
  def get_all_classes():
    """returns instances of all the table class values"""
    result = list()
    table_names = AttributeDefinition.get_all_table_names()
    for table_name in table_names:
      result.append(ValueBroker.get_class_by_string(table_name))
    return result

  def __set_class_by_attribute(self, attribute):
    """
    sets class for the attribute

    :param attribute: the attribute in context
    :type attribute: Attribute
    """
    self.__clazz = self.get_class_by_attribute(attribute)

  def __convert_attr_value_to_value(self, attribute, is_insert=True):
    """
    converts an Attribute to a Value object

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns: Value
    """
    value_instance = self.__clazz()
    value_instance.value = attribute.plain_value
    if not is_insert:
      value_instance.identifier = attribute.value_id
    value_instance.attribute_id = attribute.identifier
    value_instance.attribute = attribute
    value_instance.event_id = attribute.object.event_id
    return value_instance

  def get_by_attribute(self, attribute):
    """
    fetches one Value instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : Value
    """

    self.__set_class_by_attribute(attribute)

    try:
      clazz = self.get_broker_class()
      result = self.session.query(clazz).filter(
              clazz.attribute_id == attribute.identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'No value found with ID :{0} in {1}'.format(
                                  attribute.identifier, self.get_broker_class()))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
        'Too many value found for ID :{0} in {1}'.format(attribute.identifier,
           self.get_broker_class()))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    return result

  def inser_by_attribute(self, attribute, commit=True):
    """
    Inserts one Value instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : Value
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException(u'Attribute to be inserted is invalid')

    self.__set_class_by_attribute(attribute)
    value = self.__convert_attr_value_to_value(attribute, True)
    value.identifier = None
    BrokerBase.insert(self, value, commit)

  def update_by_attribute(self, attribute, commit=True):
    """
    updates one Value instance with the information of the given attribute

    :param attribute: the attribute in context
    :type attribute: Attribute

    :returns : Value
    """
    errors = not attribute.validate()
    if errors:
      raise ValidationException(u'Attribute to be updated is invalid')

    self.__set_class_by_attribute(attribute)
    value = self.__convert_attr_value_to_value(attribute, False)
    BrokerBase.update(self, value, commit)

  def remove_by_attribute(self, attribute, commit):
    """
    Removes one Value with the information given by the attribute

    :param attribute: the attribute in context
    :type attribute: Attribute
    :param commit: do a commit after
    :type commit: Boolean
    """
    self.__set_class_by_attribute(attribute)

    try:
      self.session.query(self.get_broker_class()).filter(
                    self.get_broker_class().attribute_id == attribute.identifier
                      ).delete(synchronize_session='fetch')
      self.do_commit(commit)
    except sqlalchemy.exc.OperationalError as error:
      self.session.rollback()
      raise IntegrityException(error)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def look_for_value(self, clazz, value):
    """
    returns a list of matching values

    :param clazz: Class to use for the lookup
    :type clazz: Class
    :param value: Value to look for
    :type value: String

    :returns: List of clazz
    """
    try:
      return self.session.query(clazz).filter(
                      clazz.value == value
                      ).all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
