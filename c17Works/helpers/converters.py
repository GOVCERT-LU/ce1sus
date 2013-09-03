# -*- coding: utf-8 -*-

"""
module used for converting values or object attributes

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from c17Works.helpers.debug import Log
import c17Works.helpers.string as string

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
    try:
      setattr(instance, attribtue, unicode(value, 'utf-8', errors='replace'))
    except ValueError as e:
      setattr(instance, attribtue, None)
      Log.getLogger("ObjectConverter").error(e)

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
    try:
      setattr(instance, attribtue, int(value))
    except ValueError as e:
      setattr(instance, attribtue, None)
      Log.getLogger("ObjectConverter").error(e)

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
    try:
      setattr(instance, attribtue, string.stringToDateTime(value))
    except ValueError as e:
      setattr(instance, attribtue, None)
      Log.getLogger("ObjectConverter").error(e)


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
      Log.getLogger("ValueConverter").error(e)
      return None

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
      return int(value)
    except ValueError as e:
      Log.getLogger("ValueConverter").error(e)
      return None

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
    except ValueError as e:
      Log.getLogger("ValueConverter").error(e)
      return None

