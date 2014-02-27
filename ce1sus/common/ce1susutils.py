# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 2, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


import ast
from dagr.helpers.converters import ValueConverter
import re
from dagr.helpers.validator.valuevalidator import ValueValidator


# The releases are formated as A.B.C where A,B,C are defined as follows
# A: Major Release
# B: Release feature changes
# C: Bug fixes
APP_REL = '0.8.2'
DB_REL = '0.8.3'
REST_REL = '0.2.0'


def convert_string_to_value(string):
  """Returns the python value of the given string"""
  return_value = None
  if string:
    if string == 'True':
      return_value = True
    elif string == 'False':
      return_value = False
    elif string.isdigit():
      return_value = ValueConverter.set_integer(string)
    # check if datetime
    elif ValueValidator.validateDateTime(string):
      return_value = ValueConverter.set_date(string)
    # TODO: use JSON instead
    elif (re.match(r'^\[.*\]$', string, re.MULTILINE) is not None or
      re.match(r'^\{.*\}$', string, re.MULTILINE) is not None):
      return_value = ast.literal_eval(string)
    else:
      return_value = string
  return return_value


# pylint: disable=W0613
def sytem_version(context):
  """
  Just for displaing inside the leyout
  """
  return APP_REL
