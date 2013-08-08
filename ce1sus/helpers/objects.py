"""object helper module"""
import types
import datetime
from collections import Iterable
from inspect import isfunction, ismethod


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 5, 2013

class CompareException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class TypeMismatchException(CompareException):
  def __init__(self, message):
    CompareException.__init__(self, message)

class ArrayMismatchException(CompareException):
  def __init__(self, message):
    CompareException.__init__(self, message)

class ValueMismatchException(CompareException):
  def __init__(self, message):
    CompareException.__init__(self, message)

class AttributeMismatchException(CompareException):
  def __init__(self, message):
    CompareException.__init__(self, message)

def compareObjects(object1, object2, raiseExceptions=True):
  """
  Compares recursively if the two input objects are equal on their attribute basis

  :param object1: First object
  :param object2: Second object

  :returns: Boolean
  """
  result = True
  attrName = ''
  attrValue1 = ''
  attrValue2 = ''
  typeIssue = False
  listIssue = False
  inputIssue = False
  if (type(object1) != type(object2)) and not (isinstance(object1,
      types.StringTypes) and isinstance(object2, types.StringTypes)):
    result = False
    typeIssue = True
    attrValue1 = type(object1)
    attrValue2 = type(object2)
  else:

    # check if not a baseType
    if (isinstance(object1, Iterable) and not isinstance(object1,
                types.StringTypes)) and (isinstance(object1, Iterable) and
                not isinstance(object1, types.StringTypes)):
      listIssue = True
      inputIssue = True

      if (len(object1) != len(object2)):
        attrName = 'length of Array'

        attrValue1 = len(object1)
        attrValue2 = len(object2)
        result = False
      else:
        if (isinstance(object1, types.DictionaryType) and
                      isinstance(object2, types.DictionaryType)):
          for key, item1 in object1.iteritems():
            if object2.has_key(key):
              # This is just to know what was the problem
              attrName = 'Value not matching for key ' + key
              attrValue1 = item1
              item2 = object2[key]
              attrValue2 = item2
              result = compareObjects(item1, item2)

        else:
          for i in range(0, len(object1)):
            item1 = object1[i]
            item2 = object2[i]
            if not compareObjects(item1, item2):
              result = False


              attrValue1 = object1[i]
              attrValue2 = object2[i]
              break

    elif ((isinstance(object1, types.StringTypes) or isinstance(object1,
                                                                types.IntType)
                or isinstance(object1, types.FloatType) or isinstance(object1,
                                                                types.LongType)
                or isinstance(object1, types.TupleType)) and
                (isinstance(object2, types.StringTypes) or isinstance(object2,
                                                                types.IntType)
                or isinstance(object2, types.FloatType) or isinstance(object2,
                                                                types.LongType)
                or isinstance(object2, types.TupleType))):
      inputIssue = True
      if object1 != object2:
        attrValue1 = object1
        attrValue2 = object2
        result = False

    elif  (isinstance(object1, datetime.datetime)) and (isinstance(object2,
                                                            datetime.datetime)):
      if object1.strftime('%Y%m%d_%H%M%S') != object2.strftime('%Y%m%d_%H%M%S'):
        attrValue1 = object1
        attrValue2 = object2
        result = False
    else:
      if not ((isinstance(object1, types.NoneType) and isinstance(object2,
                                                            types.NoneType))):
        for name in vars(object1).iterkeys():
          # only compare public attributes/functions
          value1 = None
          if not name.startswith('_'):
            # first object
            value1 = None
            if hasattr(object1, name) and hasattr(object2, name):
              value1 = getattr(object1, name)
              value2 = getattr(object2, name)

              # functions/methods will not be compared
              if (not isfunction(value1) and not isinstance(value1,
                                                            types.FunctionType)
                and not ismethod(value1)) and (not isfunction(value2) and
                                      not isinstance(value2, types.FunctionType)
                and not ismethod(value2)):
                attrName = name
                attrValue1 = value1
                attrValue2 = value2

                if not compareObjects(value1, value2, raiseExceptions):
                  result = False
                else:
                  # do nothing if it's a function
                  pass

            else:
              result = False

  if not result:
    if raiseExceptions:
      if (typeIssue):
        raise TypeMismatchException(
                      'Types differ, got {0} expected {1}'.format(attrValue1,
                                                                  attrValue2))
      elif (listIssue):
        raise ArrayMismatchException(
                      'Arrays differ, got {0} expected {1}'.format(attrValue1,
                                                                   attrValue2))
      elif (inputIssue):
        raise ValueMismatchException('Got {0} expected {1}'.format(attrValue1,
                                                                   attrValue2))
      else:
        raise AttributeMismatchException(
                      'Attribute {0} is not equal, got {1} expected {2}'.format(
                                                                    attrName,
                                                                    attrValue1,
                                                                    attrValue2))
  # if this is reached they have to be equal.
  return result


def printObject(obj, indent=0, maxRecLVL=3):
  """
  Compares recursively if the two input objects are equal on their attribute
  basis

  :param obj: object to print
  :type obj: instance of object
  :param indent: level of indentation to start it should be 0
  :type indent: Integer
  :param maxRecLVL: level of maximal recursion
  :type maxRecLVL: Integer
  :returns: Boolean
  """
  # generate indentation
  indentStr = '\t' * indent

  if (indent == 0):
    print '{indentation}{variableName}'.format(indentation=indentStr,
                                                 variableName=type(obj))

  if (indent > maxRecLVL):
    print '{indentation}...'.format(indentation=indentStr)
    return
  for name in vars(type(obj)).iterkeys():
    # Not interested in private or protected attributes
    if not name.startswith('_'):
      value = None
      if hasattr(obj, name):
        value = getattr(obj, name)
      else:
        value = 'None'
      if (isinstance(value, types.NoneType)):
        value = 'None'
      # Not interested in functions or methods
      if (not isfunction(value) and not isinstance(value, types.FunctionType)
          and not ismethod(value)):
        # If it is an list or array
        if isinstance(value, Iterable) and not isinstance(value,
                                                          types.StringTypes):

          if len(value) == 0:
            print '{indentation}{variableName}: Empty'.format(
                                                        indentation=indentStr,
                                                        variableName=name)
          else:
            for item in value:
              print '{indentation}{variableName} {type} :'.format(
                                                  indentation=indentStr,
                                                  variableName=name,
                                                  type=type(item))
              printObject(item, indent + 1, maxRecLVL)
        elif isinstance(value, object):
          # It should be one base type only the following ones are supported
          # to give a direct output
          if (isinstance(value, types.StringTypes) or isinstance(value,
                                                                 types.IntType)
              or isinstance(value, types.FloatType) or isinstance(value,
                                                                types.LongType)
              or isinstance(value, types.TupleType) or type(value) ==
                                                             datetime.datetime):
            print '{indentation}{variableName}\t: "{variableValue}"'.format(
                                                        indentation=indentStr,
                                                        variableName=name,
                                                        variableValue=value)
          else:
            # Ok it is a custom object
            print '{indentation}{variableName} {type} :'.format(
                                                      indentation=indentStr,
                                                      variableName=name,
                                                      type=type(value))
            printObject(value, indent + 1)
        else:
          # in any other case print it directly
          print '{indentation}{variableName}\t: "{variableValue}"'.format(
                                                      indentation=indentStr,
                                                      variableName=name,
                                                      variableValue=value)

def dictionaryToString(dictionary):
  """
  Prints a dictionary

  :param dictionary: the dictionary to output
  :type obj: Dictonary
  """
  for key in dictionary:
    print "{0} = '{1}'".format(key, dictionary[key])
