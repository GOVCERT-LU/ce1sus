import re
import types

ALNUM = '^[\\d\\w]*$'
ALNUM_WS = '^[\\d\\w ]*$'
ALPHA = '^[\\w]*$'
DATE = ''
DIGITS = '^[\\d]*$'
EMAILADDRESS = '^.+@.+\..{2,3}$'
IP = '[\\d]\\.[\\d]\\.[\\d]\\.[\\d]'

class ValidationException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)


class FailedValidation(object):
  def __init__(self, value, message):
    self.value = value
    self.error = message

  def __str__(self, *args, **kwargs):
    return self.value

def validateAlNum(obj, string, withSpaces=False):
  if withSpaces:
    return validateRegex(obj, string, ALNUM_WS, 'The value has to be alpha-numerical')
  else:
    return validateRegex(obj, string, ALNUM, 'The value has to be alpha-numerical')

def validateAlpha(obj, string):
  return validateRegex(obj, string, ALPHA, 'The value has to be alphabetical')

def validateDigits(obj, string):
  return validateRegex(obj, string, DIGITS, 'The value has to be numerical')

def validateEmailAddress(obj, string):
  return validateRegex(obj, string, EMAILADDRESS, 'The email has to be under the form (.*)@(.*).(.*){2,3}')

def validateIP(obj, string):
  return validateRegex(obj, string, IP, 'The IP address has to be under the form of X.X.X.X')

def validateRegex(obj, string, regex, errorMsg, notEmpty=True):
  if hasattr(obj, string):
    value = str(getattr(obj, string))
    result = True
    if notEmpty:
      if value:
        result = re.match('^.+$', value) is not None

      else:
        result = False
      if not result:
        setattr(obj, string, FailedValidation(value, 'The value is empty'))
    if result:
      result = re.match(regex, value) is not None
      if not result:
        setattr(obj, string, FailedValidation(value, errorMsg))
  else:
    raise ValidationException('The given object has no attribute ' + string)

def isObjectValid(obj):
  for value in vars(obj).itervalues():
    if type(value) == FailedValidation:
      return False
  return True
