"""validation module"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import re

ALNUM_BASE = r'^[\d\w{PlaceHolder}]{quantifier}$'
ALPHA_BASE = r'^[\D{PlaceHolder}]{quantifier}$'
DATE = [r'^[\d]{4}-[\d]{2}-[\d]{2}$',
        r'^[\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}$',
        r'^[\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2}$',
        r'^[\d]{4}-[\d]{2}-[\d]{2} - [\d]{2}:[\d]{2}:[\d]{2}$',
        r'^[\d]{4}-[\d]{2}-[\d]{2} - [\d]{2}:[\d]{2}$',
        r'^[\d]{2}/[\d]{2}/[\d]{4}$',
        r'^[\d]{2}/[\d]{2}/[\d]{4} - [\d]{2}:[\d]{2}$',
        r'^[\d]{2}/[\d]{2}/[\d]{4} - [\d]{2}:[\d]{2}:[\d]{2}$',
        r'^[\d]{2}/[\d]{2}/[\d]{4} [\d]{2}:[\d]{2}$',
        r'^[\d]{2}/[\d]{2}/[\d]{4} [\d]{2}:[\d]{2}:[\d]{2}$',
        r'^[\d]{4}-[\d]{2}-[\d]{2} [\d]{2}:[\d]{2}:[\d]{2}\.[\d]{6}$'
       ]
DIGITS = r'^[\d.]+$'
EMAILADDRESS = r'^.+@.+\..{2,3}$'
IP = r'^[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}\.[\d]{1,3}$'
HASHES = {'MD5':r'^[0-9a-fA-F]{32}$',
               'SHA1':r'^[0-9a-fA-F]{40}$',
               'SHA256':r'^[0-9a-fA-F]{64}$',
               'SHA384':r'^[0-9a-fA-F]{96}$',
               'SHA512':r'^[0-9a-fA-F]{128}$'}


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
    value = unicode(getattr(obj, attributeName))
    result = re.match(regex, value, re.UNICODE) is not None
    if not result and changeAttribute:
      setattr(obj, attributeName, FailedValidation(value, errorMsg))

    return result
  else:
    raise ValidationException('The given object has no attribute ' +
                               attributeName)


class ValidationException(Exception):
  """Validation Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)


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
                    withNonPrintableCharacters=False):
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
                                         printable characters as tab newlines etc.
      :type withNonPrintableCharacters: Boolean

      :return Boolean
    """

    obj = Container(string)
    return ObjectValidator.validateAlNum(obj,
                                    'value',
                                    minLength,
                                    maxLength,
                                    withSpaces,
                                    withNonPrintableCharacters,
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
                                         printable characters as tab newlines etc.
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
    return ObjectValidator.validateDateTime(obj, 'value', changeAttribute=False)

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


    typeUpper = getattr(hashType, 'upper')()

    # get regex
    regex = HASHES[typeUpper]
    obj = Container(string)
    return validateRegex(obj,
                  'value',
                  regex,
                  'The entered hash is not a valid {0} hash'.format(typeUpper),
                  changeAttribute=False)

class ObjectValidator:

  """
  Utility Class for validating object attributes types
  """
  def __init__(self):
    pass

  @staticmethod
  def __replacePlaceHolders(baseRegex, minLength=0,
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
    if withSpaces and not withNonPrintableCharacters:
      placeHolder += ' '
    if withSymbols:
      placeHolder += r'!$%^&*()_+|~\-={}\[\]:";\'<>?,.\/\\'

    quantifier = ''
    if minLength != 0 and maxLength != 0:
      quantifier = '{{{0},{1}}}'.format(minLength, maxLength)
    if minLength != 0 and maxLength == 0:
      quantifier = '{{{0},}}'.format(minLength)
    if minLength == 0 and maxLength != 0:
      quantifier = '{{{0}}}'.format(maxLength)
    if minLength == 0 and maxLength == 0:
      quantifier = '*'.format(minLength, maxLength)

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
    for value in vars(obj).itervalues():
      if type(value) == FailedValidation:
        return False
    return True

  @staticmethod
  def validateAlNum(obj,
                    attributeName,
                    minLength=0,
                    maxLength=0,
                    withSpaces=False,
                    withNonPrintableCharacters=False,
                    changeAttribute=True,
                    withSymbols=False):
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
                                         printable characters as tab newlines etc.
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
                                         printable characters as tab newlines etc.
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
    if minimal > 0:
      errorMsg += 'Smaller or equal than {0}.'.format(minimal)
    if maximal > 0:
      errorMsg += 'Bigger or equal than {0}'.format(maximal)

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

      result = True
      if not minimal is None and result:
        result = value >= minimal
      if not maximal is None and result:
        result = value <= maximal
      if not result:
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
    return True
    for dateFormat in DATE:
      result = validateRegex(obj,
                attributeName,
                dateFormat,
                ('The date is not under the right form as i.e. ' +
                 '"YYYY-mm-dd - H:M:S" where " - H:M:S" is optional'),
                changeAttribute)
      if result:
        break

    return result

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

    # get regex
    regex = HASHES[typeUpper]

    return validateRegex(obj,
                  attributeName,
                  regex,
                  'The entered hash is not a valid {0} hash'.format(typeUpper),
                  changeAttribute)



