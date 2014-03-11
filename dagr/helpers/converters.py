# -*- coding: utf-8 -*-

"""
module used for converting values or object attributes

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import dagr.helpers.strings as strings
import re
from dagr.helpers.validator.valuevalidator import ValueValidator
import ast


def convert_string_to_value(string):

  """Returns the python value of the given string"""
  return_value = None
  if string:
    if string == 'True':
      return_value = True
    elif string == 'False':
      return_value = False
    elif string.isdigit():
      return_value = ValueConverter.set_integer(string)
    # check if datetime
    elif ValueValidator.validateDateTime(string):
      return_value = ValueConverter.set_date(string)
    # TODO: use JSON instead
    elif (re.match(r'^\[.*\]$', string, re.MULTILINE) is not None or
      re.match(r'^\{.*\}$', string, re.MULTILINE) is not None):
      return_value = ast.literal_eval(string)
    else:
      return_value = string
  return return_value


class ConversionException(Exception):
  """Configuration Exception"""
  pass


class ValueConverter(object):
  """Converter for single values"""
  @staticmethod
  def set_string(value):
    """
    Returns a strings value of the value

    Note: If it is not possible to set the value returned value is None

    :param value: The value to be set
    :type value: strings (at least should be)

    :returns: strings
    """
    try:
      return unicode(value, 'utf-8', errors='replace')
    except ValueError as error:
      raise ConversionException(error)

  @staticmethod
  def set_integer(value):
    """
    Returns an Integer value of the value

    Note: If it is not possible to set the value returned value is None

    :param value: The value to be set
    :type value: Integer (at least should be)

    :returns: Integer
    """
    try:
      if value is None:
        return None
      str_value = '{0}'.format(value)
      if str_value:
        return int(str_value)
      else:
        return None
    except ValueError as error:
      raise ConversionException(error)

  @staticmethod
  def set_date(value):
    """
    Returns an DateTime value of the value

    Note: If it is not possible to set the value returned value is None

    :param value: The value to be set
    :type value: DateTime (at least should be)

    :returns: DateTime
    """
    try:
      return strings.stringToDateTime(value)
    except Exception as error:
      raise ConversionException(error)


class ObjectConverter(object):
  """Converter for objects"""

  @staticmethod
  def set_string(instance, attribtue, value):
    """
    Sets a strings attribute

    Note: If it is not possible to set the value the attribute is set to None

    :param instance: The instance which attribute has to be set
    :type instance: object
    :param attribute: The name of the attribute to set
    :type: attribute: strings
    :param value: The value to be set
    :type value: strings (at least should be)
    """
    setattr(instance, attribtue, ValueConverter.set_string(value))

  @staticmethod
  def set_integer(instance, attribtue, value):
    """
    Sets a Integer attribute

    Note: If it is not possible to set the value the attribute is set to None

    :param instance: The instance which attribute has to be set
    :type instance: object
    :param attribute: The name of the attribute to set
    :type: attribute: Integer
    :param value: The value to be set
    :type value: Integer (at least should be)
    """
    try:
      setattr(instance, attribtue, ValueConverter.set_integer(value))
    except AttributeError:
      pass

  @staticmethod
  def set_date(instance, attribtue, value):
    """
    Sets a date time attribute

    Note: If it is not possible to set the value the attribute is set to None

    :param instance: The instance which attribute has to be set
    :type instance: object
    :param attribute: The name of the attribute to set
    :type: attribute: Datetime
    :param value: The value to be set
    :type value: DateTime strings (at least should be)
    """
    setattr(instance, attribtue, ValueConverter.set_date(value))
