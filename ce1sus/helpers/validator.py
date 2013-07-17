import re
import types

ALNUM='^[\\d\\w]*$'
ALPHA='^[\\w]*$'
DATE=''
DIGITS='^[\\d]*$'
EMAILADDRESS='^.+@.+\..{2,3}$'
IP='[\\d]\\.[\\d]\\.[\\d]\\.[\\d]'

class ValidationException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)


class FailedValidation(object):
  def __init__(self, value, message):
    self.value = value
    self.error = message
    
  def __str__(self, *args, **kwargs):
    return self.value

def validateAlNum(obj, attribute):
  return validateRegex(obj, attribute, ALNUM, 'The value has to be alpha-numerical')

def validateAlpha(obj, attribute):
  return validateRegex(obj, attribute, ALPHA, 'The value has to be alphabetical')

def validateDigits(obj, attribute):
  return validateRegex(obj, attribute, DIGITS, 'The value has to be numerical')

def validateEmailAddress(obj, attribute):
  return validateRegex(obj, attribute, EMAILADDRESS, 'The email has to be under the form (.*)@(.*).(.*){2,3}')

def validateIP(obj, attribute):
  return validateRegex(obj, attribute, IP, 'The IP address has to be under the form of X.X.X.X')

def validateRegex(obj, attribute, regex, errorMsg, notEmpty=True): 
  if hasattr(obj, attribute):
    value = getattr(obj, attribute)
    result = True
    if notEmpty:
      if type(value) is types.NoneType:
        result = False
      else:
        result = re.match('^.+$', value) is not None
      if not result:
        setattr(obj, attribute, FailedValidation(value,'The value is empty')) 
    if result:
      result = re.match(regex, value) is not None
      if not result:
        setattr(obj, attribute, FailedValidation(value,errorMsg)) 
  else:
    raise ValidationException('The given object has no attribute '+attribute)
  
def isObjectValid(obj):
  for name, value in vars(obj).items():
    if type(value) == FailedValidation:
      return False
  return True