# -*- coding: utf-8 -*-

"""
object helper module

Created on Jul 5, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import types
import datetime
from collections import Iterable
from inspect import isfunction, ismethod
from importlib import import_module


class GenObject(object):
    pass


def get_class(modulename, classname):
  """returns the class name from a string"""
  splited_modulename = modulename.rsplit('.', 1)
  if len(splited_modulename) > 1:
    module_name = '.' + splited_modulename[1]
    package = splited_modulename[0]
  else:
    module_name = modulename
    package = ''
  module = import_module(module_name, package)
  clazz = getattr(module, classname)
  return clazz


class CompareException(Exception):
  """
  Base compare exception
  """
  pass


class PrintException(Exception):
  """
  Base compare exception
  """
  pass


class TypeMismatchException(CompareException):
  """
  Type mismatch exception
  """
  pass


class ArrayMismatchException(CompareException):
  """
  Array mismatch exception
  """
  pass


class ValueMismatchException(CompareException):
  """
  Value mismatch exception
  """
  pass


class AttributeMismatchException(CompareException):
  """
  Attribute mismatch exception
  """
  pass


def get_fields(obj):
  """Returns the attributes of an object"""
  fields = list()
  for name in vars(type(obj)).iterkeys():
    # if not a private or protected value and not a method
      if not name.startswith('_') and not callable(getattr(obj, name, None)):
        fields.append(name)
  if hasattr(obj, '__dict__'):
    for name in obj.__dict__:
      # if not a private or protected value and not a method
      if not name.startswith('_') and not callable(getattr(obj, name, None)):
        if name not in fields:
          fields.append(name)
  return fields


def get_methods(obj):
  """Returns the attributes of an object"""
  methods = list()
  for name in vars(type(obj)).iterkeys():
    # if not a private or protected value and not a method
      if not name.startswith('_') and callable(getattr(obj, name, None)):
        methods.append(name)
  if hasattr(obj, '__dict__'):
    for name in obj.__dict__:
      # if not a private or protected value and not a method
      if not name.startswith('_') and callable(getattr(obj, name, None)):
        if name not in methods:
          methods.append(name)
  return methods


def compare_objects(object1, object2, raise_exceptions=True):
  """
  Compares recursively if the two input objects are equal on their attribute
  basis

  :param object1: First object
  :param object2: Second object

  :returns: Boolean
  """
  result = True
  attr_name = ''
  attr_value1 = ''
  attr_value2 = ''
  type_issue = False
  list_issue = False
  input_issue = False
  if (type(object1) != type(object2)) and not (isinstance(object1,
                                                          types.StringTypes) and
                                               isinstance(object2, types.StringTypes)):
    result = False
    type_issue = True
    attr_value1 = type(object1)
    attr_value2 = type(object2)
  else:
    # check if not a baseType
    if (isinstance(object1, Iterable) and not isinstance(object1,
                                                         types.StringTypes)) and (isinstance(object1, Iterable) and
                                                                                  not isinstance(object1, types.StringTypes)):
      list_issue = True
      input_issue = True
      if (len(object1) != len(object2)):
        attr_name = 'length of Array'
        attr_value1 = len(object1)
        attr_value2 = len(object2)
        result = False
      else:
        if (isinstance(object1, types.DictionaryType) and isinstance(object2, types.DictionaryType)):
          for key, item1 in object1.iteritems():
            if key in object2:
              # This is just to know what was the problem
              attr_name = 'Value not matching for key ' + key
              attr_value1 = item1
              item2 = object2[key]
              attr_value2 = item2
              result = compare_objects(item1, item2)
        else:
          for i in range(0, len(object1)):
            item1 = object1[i]
            item2 = object2[i]
            if not compare_objects(item1, item2):
              result = False
              attr_value1 = object1[i]
              attr_value2 = object2[i]
              break
    elif ((isinstance(object1, types.StringTypes) or
           isinstance(object1, types.IntType) or
           isinstance(object1, types.FloatType) or
           isinstance(object1, types.LongType) or
           isinstance(object1, types.TupleType)) and
          (isinstance(object2, types.StringTypes) or isinstance(object2, types.IntType) or
           isinstance(object2, types.FloatType) or isinstance(object2, types.LongType) or
           isinstance(object2, types.TupleType))):
      input_issue = True
      if object1 != object2:
        attr_value1 = object1
        attr_value2 = object2
        result = False
    elif (isinstance(object1, datetime.datetime)) and (isinstance(object2, datetime.datetime)):
      if (object1.strftime('%Y%m%d_%H%M%S') != object2.strftime('%Y%m%d_%H%M%S')):
        attr_value1 = object1
        attr_value2 = object2
        result = False
    else:
      if not ((isinstance(object1, types.NoneType) and isinstance(object2, types.NoneType))):
        for name in get_fields(object1):
          # only compare public attributes/functions
          value1 = None
          if not name.startswith('_'):
            # first object
            value1 = None
            if hasattr(object1, name) and hasattr(object2, name):
              value1 = getattr(object1, name)
              value2 = getattr(object2, name)
              # functions/methods will not be compared
              if (not isfunction(value1) and not isinstance(value1, types.FunctionType)
                  and not ismethod(value1)) and (not isfunction(value2) and
                                                 not isinstance(value2, types.FunctionType)
                                                 and not ismethod(value2)):
                attr_name = name
                attr_value1 = value1
                attr_value2 = value2
                if compare_objects(value1, value2, raise_exceptions):
                  result = True

                else:
                  # do nothing if it's a function
                  result = False
            else:
              result = False
  if not result:
    if raise_exceptions:
      if (type_issue):
        raise TypeMismatchException('Types differ, got {0} expected {1}'.format(attr_value1,
                                                                                attr_value2))
      elif (list_issue):
        raise ArrayMismatchException('Arrays differ, got {0} expected {1}'.format(attr_value1,
                                                                                  attr_value2))
      elif (input_issue):
        raise ValueMismatchException('Got {0} expected {1}'.format(attr_value1,
                                                                   attr_value2))
      else:
        raise AttributeMismatchException('Attribute {0} is not equal, got {1} expected {2}'.format(attr_name,
                                                                                                   attr_value1,
                                                                                                   attr_value2))
  # if this is reached they have to be equal.
  return result


def print_object(obj, indent=0, max_rec_lvl=3):
  """
  Compares recursively if the two input objects are equal on their attribute
  basis

  :param obj: object to print
  :type obj: instance of object
  :param indent: level of indentation to start it should be 0
  :type indent: Integer
  :param max_rec_lvl: level of maximal recursion
  :type max_rec_lvl: Integer
  :returns: Boolean
  """
  if not isinstance(obj, object):
    raise PrintException('The object to be printed is not an object')
  # generate indentation
  indent_str = '\t' * indent
  if (indent == 0):
    print '{indentation}{variableName}'.format(indentation=indent_str,
                                               variableName=type(obj))
  if (indent > max_rec_lvl):
    print '{indentation}...'.format(indentation=indent_str)
    return
  for name in get_fields(obj):
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
      if (not isfunction(value) and not isinstance(value, types.FunctionType)and not ismethod(value)):
        # If it is an list or array
        if isinstance(value, Iterable) and not isinstance(value,
                                                          types.StringTypes):
          if len(value) == 0:
            print '{indentation}{variableName}: Empty'.format(indentation=indent_str,
                                                              variableName=name)
          else:
            for item in value:
              print '{indentation}{variableName} {type} :'.format(indentation=indent_str,
                                                                  variableName=name,
                                                                  type=type(item))
              print_object(item, indent + 1, max_rec_lvl)
        elif isinstance(value, object):
          # It should be one base type only the following ones are supported
          # to give a direct output
          if (isinstance(value, types.StringTypes) or
              isinstance(value, types.IntType) or
              isinstance(value, types.FloatType) or
              isinstance(value, types.LongType) or
              isinstance(value, types.TupleType) or
              type(value) == datetime.datetime
              ):
            print '{indentation}{variableName}\t: "{variableValue}"'.format(indentation=indent_str,
                                                                            variableName=name,
                                                                            variableValue=value)
          else:
            # Ok it is a custom object
            print '{indentation}{variableName} {type} :'.format(indentation=indent_str,
                                                                variableName=name,
                                                                type=type(value))
            print_object(value, indent + 1)
        else:
          # in any other case print it directly
          print '{indentation}{variableName}\t: "{variableValue}"'.format(indentation=indent_str,
                                                                          variableName=name,
                                                                          variableValue=value)


def print_dictionary(dictionary):
  """
  Prints a dictionary

  :param dictionary: the dictionary to output
  :type obj: Dictonary
  """
  for key, value in dictionary.iteritems():
    print "{0} = '{1}'".format(key, value)
