# -*- coding: utf-8 -*-

"""
validation module

Created Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import re
from sre_constants import error
from dagr.helpers.strings import stringToDateTime, InputException
import datetime
from dagr.helpers.objects import get_fields

ALNUM_BASE = r'^[\d\w{PlaceHolder}]{quantifier}$'
ALPHA_BASE = r'^[\D{PlaceHolder}]{quantifier}$'
DIGITS = r'^[\d.]+$'
EMAILADDRESS = r'^.+@.+\..{2,3}$'
IP = r'^[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}$'
HASHES = {'MD5': r'^[0-9a-fA-F]{32}$',
               'SHA1': r'^[0-9a-fA-F]{40}$',
               'SHA256': r'^[0-9a-fA-F]{64}$',
               'SHA384': r'^[0-9a-fA-F]{96}$',
               'SHA512': r'^[0-9a-fA-F]{128}$'}


def validateRegex(obj, attributeName, regex, errorMsg, changeAttribute=False):
  """
    Validates the attribute attributeName of the object obj against the regex.

    Note: The actual object is changed internally

    :param obj: Object
    :type obj: object
    :param attributeName: attribute name of the object
    :type attributeName: String
    :param errorMsg: Error message to be shown is case of a failed validation
    :type errorMsg: String
    :param changeAttribute: If set the given attribute will be changed to a
                            type of FailedValidation
    :type changeAttribute: Boolean
  """
  if hasattr(obj, attributeName):
    value = getattr(obj, attributeName, '')
    stringValue = u'{0}'.format(value)
    stringValue = stringValue.strip()
    result = re.match(regex, stringValue, re.MULTILINE) is not None
    if not result and changeAttribute:
      setattr(obj, attributeName, FailedValidation(stringValue, errorMsg))

    return result
  else:
    raise ValidationException('The given object has no attribute ' +
                               attributeName)


class ValidationException(Exception):
  """Validation Exception"""
  pass


# pylint: disable=R0903
class FailedValidation(object):
  """
  Failed Validation Class

  Note: A failed validation is replaced by this class
  """
  def __init__(self, value, message):
    self.value = value
    self.error = message

  def __str__(self, *args, **kwargs):
    return self.value


class ObjectValidator:
  """
  Utility Class for validating object attributes types
  """
  def __init__(self):
    pass

  # pylint: disable=R0913
  @staticmethod
  def __replacePlaceHolders(baseRegex,
                            minLength=0,
                            maxLength=0,
                            withSpaces=False,
                            withNonPrintableCharacters=False,
                            withSymbols=False):
    """
    Replaces the place holders of the regexes
    """
    placeHolder = ''
    if withNonPrintableCharacters:
      placeHolder += r'\s'
    else:
      if withSpaces:
        placeHolder += ' '
    if withSymbols:
      placeHolder += r'\W'

    quantifier = ''
    if minLength != 0 and maxLength != 0:
      quantifier = '{{{0},{1}}}'.format(minLength, maxLength)
    elif minLength == 0 and maxLength == 0:
      quantifier = '*'.format(minLength, maxLength)
    elif maxLength == 0:
      quantifier = '{{{0},}}'.format(minLength)
    elif minLength == 0:
      quantifier = '{{{0}}}'.format(maxLength)

    return baseRegex.format(PlaceHolder=placeHolder, quantifier=quantifier)

  @staticmethod
  def isObjectValid(obj):
    """
      Checks if an object is valid. This means that the object has
      no attribute of type FailedValidation

      :param obj: The object instance to be tested
      :type obj: object

      :returns: Boolean
    """
    fields = get_fields(obj)
    for field_name in fields:
      value = getattr(obj, field_name)
      if type(value) == FailedValidation:
        return False
    return True

  @staticmethod
  def getFirstValidationError(obj):
    fields = get_fields(obj)
    for field_name in fields:
      value = getattr(obj, field_name)
      if type(value) == FailedValidation:
        attributeName = field_name[field_name.rfind('_') + 1:]
        return 'Attribute "{0}" is invalid due to: {1}'.format(attributeName, value.error)
    return ''

  @staticmethod
  def validateAlNum(obj,
                    attributeName,
                    minLength=0,
                    maxLength=0,
                    withSpaces=False,
                    withNonPrintableCharacters=False,
                    withSymbols=False,
                    changeAttribute=True):
    """
      Validates if the attribute is of an alphanumeric kind.

      Note: The actual object is changed internally

      :param obj: Object
      :type obj: object
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param minLength: The minimal length of the string
      :type minLength: Integer
      :param maxLength: The maximal length of the string
      :type maxLength: Integer
      :param withSpaces: If set the attribute can contain spaces
      :type withSpaces: Boolean
      :param withNonPrintableCharacters: If set the attribute can contain non
                                         printable characters as tab newlines
                                         etc.
      :type withNonPrintableCharacters: Boolean
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """
    errorMsg = 'The value has to be alpha-numerical'
    if withSymbols:
      errorMsg += ' incl. Symbols.'
    else:
      errorMsg += '.'
    if minLength > 0:
      errorMsg += 'A minimal length of {0}.'.format(minLength)
    if maxLength > 0:
      errorMsg += 'A maximal length of {0}'.format(maxLength)

    regex = ObjectValidator.__replacePlaceHolders(ALNUM_BASE,
                                                  minLength,
                                                  maxLength,
                                                  withSpaces,
                                                  withNonPrintableCharacters,
                                                  withSymbols)
    return validateRegex(obj, attributeName, regex, errorMsg, changeAttribute)

  @staticmethod
  def validateAlpha(obj,
                    attributeName,
                    minLength=0,
                    maxLength=0,
                    withSpaces=False,
                    withNonPrintableCharacters=False,
                    changeAttribute=True,
                    withSymbols=False):
    """
      Validates if the attribute is of an alphabetical kind.

      Note: The actual object is changed internally

      :param obj: Object
      :type obj: object
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param minLength: The minimal length of the string
      :type minLength: Integer
      :param maxLength: The maximal length of the string
      :type maxLength: Integer
      :param withSpaces: If set the attribute can contain spaces
      :type withSpaces: Boolean
      :param withNonPrintableCharacters: If set the attribute can contain non
                                         printable characters as tab newlines
                                         etc.
      :type withNonPrintableCharacters: Boolean
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """

    errorMsg = 'The value has to be alphabetical'
    if withSymbols:
      errorMsg += '  incl. Symbols.'
    else:
      errorMsg += '.'
    if minLength > 0:
      errorMsg += 'A minimal length of {0}.'.format(minLength)
    if maxLength > 0:
      errorMsg += 'A maximal length of {0}'.format(maxLength)
    regex = ObjectValidator.__replacePlaceHolders(ALPHA_BASE,
                                                  minLength,
                                                  maxLength,
                                                  withSpaces,
                                                  withNonPrintableCharacters,
                                                  withSymbols)
    return validateRegex(obj, attributeName, regex, errorMsg, changeAttribute)

  @staticmethod
  def validateDigits(obj,
                     attributeName,
                     minimal=None,
                     maximal=None,
                     changeAttribute=True):
    """
      Validates if the attribute is of an numerical kind.

      Note: The actual object is changed internally

      :param obj: Object
      :type obj: object
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param minimal: the minimal value the number
      :type minimal: Number
      :param maximal: the maximal value the number
      :type maximal: Number
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """
    errorMsg = 'The value has to be numerical.'
    result = validateRegex(obj,
                           attributeName,
                           DIGITS,
                           errorMsg,
                           changeAttribute)
    if result:
      # if this is reached the object is valid
      try:
        value = float(getattr(obj, attributeName))
      except ValueError:
        return False

      if minimal and maximal:
        errorMsg += ('Smaller or equal than {0} and bigger or equal'
                     + ' than {0}').format(minimal, maximal)
        result = minimal <= value <= maximal
      elif maximal:
        errorMsg += 'Bigger or equal than {0}'.format(maximal)
        result = value <= maximal
      else:
        errorMsg += 'Smaller or equal than {0}.'.format(minimal)
        result = value >= minimal

      if not result and changeAttribute:
        setattr(obj, attributeName, FailedValidation(value, errorMsg))

      return result

  @staticmethod
  def validateEmailAddress(obj, attributeName, changeAttribute=True):
    """
      Validates if the attribute is an email.

      Note: The actual object is changed internally

      :param obj: Object
      :type obj: object
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """
    return validateRegex(obj,
                  attributeName,
                  EMAILADDRESS,
                  'The email has to be under the form (.*)@(.*).(.*){2,3}',
                  changeAttribute)

  @staticmethod
  def validateIP(obj, attributeName, changeAttribute=True):
    """
      Validates if the attribute is an IP address.

      Note: The actual object is changed internally

      :param obj: Object
      :type obj: object
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """
    return validateRegex(obj,
                  attributeName,
                  IP,
                  'The IP address has to be under the form of X.X.X.X',
                  changeAttribute)

  @staticmethod
  def validateDateTime(obj, attributeName, changeAttribute=True):
    """
      Validates if the attribute is a date or date time under the
      specified formats address.

      Note: The actual object is changed internally

      :param obj: Object
      :type obj: object
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """
    errorMsg = ('The date is not under the right form as i.e. ' +
                 '"YYYY-mm-dd - H:M:S" where " - H:M:S" is optional')

    value = getattr(obj, attributeName)
    if isinstance(value, datetime.datetime):
      return True
    try:
      if ObjectValidator.validateIP(obj, attributeName, False):
        return False
      stringToDateTime(value)
      return True
    except InputException as e:
      if changeAttribute:
        setattr(obj, attributeName, FailedValidation(value, errorMsg))
      return False


  @staticmethod
  def validateRegex(obj, attributeName, regex, errorMsg, changeAttribute=True):
    """
    wrapper for validateRegex
    """
    return validateRegex(obj, attributeName, regex, errorMsg, changeAttribute)

  @staticmethod
  def validateHash(obj, attributeName, hashType, changeAttribute=True):
    """
      Validates if the attribute is a valid hash.

      The supported types are: MD5,SHA1,SHA256,SHA386,SHA512

      Note: The actual object is changed internally

      :param obj: Object
      :type obj: object
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param hashType: Hash type to be validated i.e 'MD5'
      :param hashType: String
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """

    typeUpper = getattr(hashType, 'upper')()

    # get regex of the hash
    regex = HASHES[typeUpper]

    return validateRegex(obj,
                  attributeName,
                  regex,
                  'The entered hash is not a valid {0} hash'.format(typeUpper),
                  changeAttribute)

  @staticmethod
  def validateRegularExpression(obj, attributeName, changeAttribute=True):
    """
      Validates if the attribute is a valid regular expression.

      Note: The actual object is changed internally

      :param obj: Object
      :type obj: object
      :param attributeName: attribute name of the object
      :type attributeName: String
      :param changeAttribute: If set the given attribute will be changed to a
                              type of FailedValidation
      :type changeAttribute: Boolean

      :return Boolean
    """
    errorMsg = 'Unknown error'
    if hasattr(obj, attributeName):
      regex = unicode(getattr(obj, attributeName))
      try:
        h = re.compile(regex)
        # remove the unneeded variable
        del h
        result = True
      except error as e:
        errorMsg = e
        result = False
      if not result and changeAttribute:
        setattr(obj,
                attributeName,
                FailedValidation(regex,
                                 ('The given regex is invalid '
                                 + 'due to: {0}').format(errorMsg)))
      return result
    else:
      raise ValidationException('The given object has no attribute ' +
                                 attributeName)
