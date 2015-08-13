from datetime import datetime, date
from decimal import Decimal
from uuid import UUID


def merge_dictionaries(dict1, dict2):
  result = dict()
  for key, value in dict1.iteritems():
    result[key] = value
  for key, value in dict2.iteritems():
    result[key] = value
  return result

def convert_value(value):
  # TODO: rethink the wrapped file foo
  """converts the value None to '' else it will be send as None-Text"""
  if value or value == 0:
    if isinstance(value, datetime):
  # return value.strftime('%m/%d/%Y %H:%M:%S %Z')
      return value.isoformat()
    if isinstance(value, date):
      # return value.strftime('%Y-%m-%d')
      return value.isoformat()
    if isinstance(value, UUID):
      return u'{0}'.format(value)
    if isinstance(value, Decimal):
      return fakefloat(value)
    return value
  else:
    return ''

class fakefloat(float):
  def __init__(self, value):
    self._value = value

  def __repr__(self):
    return str(self._value)
