# -*- coding: utf-8 -*-

"""
module used for converting values or object attributes

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import dagr.helpers.strings as string


class ConversionException(Exception):
  """Configuration Exception"""

  def __init__(self, message):
    Exception.__init__(self, message)


class ValueConverter(object):
  """Converter for single values"""
  @staticmethod
  def setString(value):
    """
    Returns a string value of the value

    Note: If it is not possible to set the value returned value is None

    :param value: The value to be set
    :type value: String (at least should be)

    :returns: String
    """
    try:
      return unicode(value, 'utf-8', errors='replace')
    except ValueError as e:
      raise ConversionException(e)

  @staticmethod
  def setInteger(value):
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
      strValue = '{0}'.format(value)
      if strValue:
        return int(strValue)
      else:
        return None
    except ValueError as e:
      raise ConversionException(e)

  @staticmethod
  def setDate(value):
    """
    Returns an DateTime value of the value

    Note: If it is not possible to set the value returned value is None

    :param value: The value to be set
    :type value: DateTime (at least should be)

    :returns: DateTime
    """
    try:
      return string.stringToDateTime(value)
    except Exception as e:
      raise ConversionException(e)


class ObjectConverter(object):
  """Converter for objects"""

  @staticmethod
  def setString(instance, attribtue, value):
    """
    Sets a string attribute

    Note: If it is not possible to set the value the attribute is set to None

    :param instance: The instance which attribute has to be set
    :type instance: object
    :param attribute: The name of the attribute to set
    :type: attribute: String
    :param value: The value to be set
    :type value: String (at least should be)
    """
    setattr(instance, attribtue, ValueConverter.setString(value))

  @staticmethod
  def setInteger(instance, attribtue, value):
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
    setattr(instance, attribtue, ValueConverter.setInteger(value))

  @staticmethod
  def setDate(instance, attribtue, value):
    """
    Sets a date time attribute

    Note: If it is not possible to set the value the attribute is set to None

    :param instance: The instance which attribute has to be set
    :type instance: object
    :param attribute: The name of the attribute to set
    :type: attribute: Datetime
    :param value: The value to be set
    :type value: DateTime string (at least should be)
    """
    setattr(instance, attribtue, ValueConverter.setDate(value))
