# -*- coding: utf-8 -*-

"""
validation module

Created Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator, validateRegex


# pylint: disable=R0903
class Container(object):
  """
  Container class

  Note:
    Should only be used by the ValueValidator
  """
  def __init__(self, value):
    self.value = value


class ValueValidator:
  """
  Utility Class for validating base types
  """
  def __init__(self):
    pass

  @staticmethod
  def validateAlNum(string,
                    minLength=0,
                    maxLength=0,
                    withSpaces=False,
                    withNonPrintableCharacters=False,
                    withSymbols=False):
    """
      Validates if the string is of an alphanumeric kind.

      :param string: The string to be validated
      :type string: String
      :param minLength: The minimal length of the string
      :type minLength: Integer
      :param maxLength: The maximal length of the string
      :type maxLength: Integer
      :param withSpaces: If set the string can contain spaces
      :type withSpaces: Boolean
      :param withNonPrintableCharacters: If set the string can contain non
                                         printable characters as tab newlines
                                         etc.
      :type withNonPrintableCharacters: Boolean

      :return Boolean
    """

    obj = Container(string)
    return ObjectValidator.validateAlNum(obj,
                                         'value',
                                         minLength=minLength,
                                         maxLength=maxLength,
                                         withSpaces=withSpaces,
                                         withNonPrintableCharacters=withNonPrintableCharacters,
                                         withSymbols=withSymbols,
                                         changeAttribute=False)

  @staticmethod
  def validateAlpha(string,
                    minLength=0,
                    maxLength=0,
                    withSpaces=False,
                    withNonPrintableCharacters=False):
    """
      Validates if the string is of an alphabetical kind.

      :param string: The string to be validated
      :type string: String
      :param minLength: The minimal length of the string
      :type minLength: Integer
      :param maxLength: The maximal length of the string
      :type maxLength: Integer
      :param withSpaces: If set the string can contain spaces
      :type withSpaces: Boolean
      :param withNonPrintableCharacters: If set the string can contain non
                                         printable characters as tab newlines
                                         etc.
      :type withNonPrintableCharacters: Boolean

      :return Boolean
    """

    obj = Container(string)
    return ObjectValidator.validateAlpha(obj,
                                         'value',
                                         minLength,
                                         maxLength,
                                         withSpaces,
                                         withNonPrintableCharacters,
                                         changeAttribute=False)

  @staticmethod
  def validateDigits(string,
                     minimal=None,
                     maximal=None):
    """
      Validates if the attribute is of an numerical kind.

      Note: The actual object is changed internally

      :param string: The string to be validated
      :type string: String
      :param minimal: the minimal value the number
      :type minimal: Number
      :param maximal: the maximal value the number
      :type maximal: Number

      :return Boolean
    """

    obj = Container(string)
    return ObjectValidator.validateDigits(obj,
                                          'value',
                                          minimal,
                                          maximal,
                                          changeAttribute=False)

  @staticmethod
  def validateEmailAddress(string):
    """
      Validates if the attribute is an email.

      Note: The actual object is changed internally

      :param string: Text to be analyzed
      :type string: String
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """

    obj = Container(string)
    return ObjectValidator.validateEmailAddress(obj,
                                                'value',
                                                changeAttribute=False)

  @staticmethod
  def validateIP(string):
    """
      Validates if the attribute is an IP address.

      Note: The actual object is changed internally

      :param string: Text to be analyzed
      :type string: String

      :return Boolean
    """
    obj = Container(string)
    return ObjectValidator.validateIP(obj, 'value', changeAttribute=False)

  @staticmethod
  def validateDateTime(string):
    """
      Validates if the attribute is a date or date time under the
      specified formats address.

      Note: The actual object is changed internally

      :param string: Text to be analyzed
      :type string: String


      :return Boolean
    """
    obj = Container(string)
    return ObjectValidator.validateDateTime(obj, 'value',
                                            changeAttribute=False)

  @staticmethod
  def validateRegex(string, regex, errorMsg):
    """
    wrapper for validateRegex
    """
    obj = Container(string)
    return validateRegex(obj, 'value', regex, errorMsg, changeAttribute=False)

  @staticmethod
  def validateHash(string, hashType):
    """
      Validates if the attribute is a valid hash.

      The supported types are: MD5,SHA1,SHA256,SHA386,SHA512

      Note: The actual object is changed internally

      :param string: Text to be analyzed
      :type string: String
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param hashType: Hash type to be validated i.e 'MD5'
      :param hashType: String

      :return Boolean
    """
    obj = Container(string)
    return ObjectValidator.validateHash(obj,
                                        'value',
                                        hashType,
                                        changeAttribute=False)

  @staticmethod
  def validateRegularExpression(regex):
    """
      Validates if the attribute is a valid regular expression.

      Note: The actual object is changed internally

      :param regex: regular expression to be validated
      :type regex: String

      :return Boolean
    """
    obj = Container(regex)
    return ObjectValidator.validateRegularExpression(obj,
                                                     'value',
                                                     changeAttribute=False)
