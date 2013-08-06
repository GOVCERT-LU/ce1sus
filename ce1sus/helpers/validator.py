"""validation module"""

import re

ALNUM = '^[\\d\\w]*$'
ALNUM_WS = '^[\\d\\w ]*$'
ALPHA = '^[\\w]*$'
ALPHA_WS = '^[\\w ]*$'
DATE = ''
DIGITS = '^[\\d]*$'
EMAILADDRESS = '^.+@.+\\..{2,3}$'
IP = '[\\d]\\.[\\d]\\.[\\d]\\.[\\d]'

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

def validateAlNum(obj, attributeName, withSpaces=False, withLineBreaks=False):
  """
    Validates if the attribute is of an alphanumeric kind.

    Note: The actual object is changed internally

    :param obj: Object
    :type obj: object
    :param attributeName: attribute name of the object
    :type attributeName: String
    :param withSpaces: If set the attribute can contain spaces
    :type withSpaces: Boolean
  """
  if withSpaces:
      return validateRegex(obj, attributeName, ALNUM_WS,
                         'The value has to be alpha-numerical')
  else:
      return validateRegex(obj, attributeName, ALNUM,
                         'The value has to be alpha-numerical')

def validateAlpha(obj, attributeName, withSpaces=False):
  """
    Validates if the attribute is of an alphabetical kind.

    Note: The actual object is changed internally

    :param obj: Object
    :type obj: object
    :param attributeName: attribute name of the object
    :type attributeName: String
    :param withSpaces: If set the attribute can contain spaces
    :type withSpaces: Boolean
  """
  if withSpaces:
    return validateRegex(obj, attributeName, ALPHA_WS,
                       'The value has to be alphabetical')
  else:
    return validateRegex(obj, attributeName, ALPHA,
                       'The value has to be alphabetical')

def validateDigits(obj, attributeName):
  """
    Validates if the attribute is of an numerical kind.

    Note: The actual object is changed internally

    :param obj: Object
    :type obj: object
    :param attributeName: attribute name of the object
    :type attributeName: String
    :param withSpaces: If set the attribute can contain spaces
    :type withSpaces: Boolean
  """
  return validateRegex(obj, attributeName, DIGITS,
                       'The value has to be numerical')

def validateEmailAddress(obj, attributeName):
  """
    Validates if the attribute is an email.

    Note: The actual object is changed internally

    :param obj: Object
    :type obj: object
    :param attributeName: attribute name of the object
    :type attributeName: String
  """
  return validateRegex(obj, attributeName, EMAILADDRESS,
                       'The email has to be under the form (.*)@(.*).(.*){2,3}')

def validateIP(obj, attributeName):
  """
    Validates if the attribute is an IP address.

    Note: The actual object is changed internally

    :param obj: Object
    :type obj: object
    :param attributeName: attribute name of the object
    :type attributeName: String
  """
  return validateRegex(obj, attributeName, IP,
                       'The IP address has to be under the form of X.X.X.X')

def validateRegex(obj, attributeName, regex, errorMsg, notEmpty=True):
  """
    Validates the attribute attributeName of the object obj against the regex.

    Note: The actual object is changed internally

    :param obj: Object
    :type obj: object
    :param attributeName: attribute name of the object
    :type attributeName: String
    :param errorMsg: Error message to be shown is case of a failed validation
    :type errorMsg: String
    :param notEmpty: If set the attribute cannot be empty
    :type notEmpty: Boolean
  """
  if hasattr(obj, attributeName):
    value = str(getattr(obj, attributeName))
    result = True
    if notEmpty:
      if value:
        result = re.match('^.+$', value) is not None

      else:
        result = False
      if not result:
        setattr(obj, attributeName, FailedValidation(value,
                                                     'The value is empty'))
    if result:
      result = re.match(regex, value) is not None
      if not result:
        setattr(obj, attributeName, FailedValidation(value, errorMsg))
  else:
    raise ValidationException('The given object has no attribute ' +
                               attributeName)

def isObjectValid(obj):
  """
    Checks if an object is valid. This means that no attribute is of type
    FailedValidation

    :returns: Boolean
  """
  for value in vars(obj).itervalues():
    if type(value) == FailedValidation:
      return False
  return True
