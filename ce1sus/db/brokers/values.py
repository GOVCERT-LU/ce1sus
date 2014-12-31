# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 23, 2014
"""
import sqlalchemy.orm.exc

from ce1sus.db.classes.common import ValueTable
from ce1sus.db.classes.definitions import AttributeDefinition
from ce1sus.db.classes.values import StringValue
from ce1sus.db.common.broker import BrokerBase, NothingFoundException, TooManyResultsFoundException, BrokerException, ValidationException, IntegrityException
from ce1sus.helpers.common.objects import get_class


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


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
    return ValueBroker.get_class_by_attr_def(attribute.definition)

  @staticmethod
  def get_class_by_string(classname):
    """
    returns class for the attribute

    :param classname: the name of the class
    :type classname: Class
    """
    return get_class('ce1sus.db.classes.values', u'{0}Value'.format(classname))

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
    table_names = ValueTable.get_all_table_names()
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
      result = self.session.query(clazz).filter(clazz.attribute_id == attribute.identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'No value found with ID :{0} in {1}'.format(
                                  attribute.identifier, self.get_broker_class()))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many value found for ID :{0} in {1}'.format(attribute.identifier,
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
      self.session.query(self.get_broker_class()).filter(self.get_broker_class().attribute_id == attribute.identifier
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
      return self.session.query(clazz).filter(clazz.value == value).all()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
