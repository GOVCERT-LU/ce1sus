# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 17, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susAPIException(Exception):
  """
  Base Exception for API Exceptions
  """
  pass


class Ce1susForbiddenException(Ce1susAPIException):
  """ Ce1susForbiddenException """
  pass


class Ce1susNothingFoundException(Ce1susAPIException):
  """ Ce1susNothingFoundException """
  pass


class Ce1susUndefinedException(Ce1susAPIException):
  """ Ce1susUndefinedException """
  pass


class Ce1susUnkownDefinition(Ce1susAPIException):
  """ Ce1susUnkownDefinition """
  pass


class Ce1susInvalidParameter(Ce1susAPIException):
  """ Ce1susInvalidParameter """
  pass


class Ce1susAPIConnectionException(Ce1susAPIException):
  """ Ce1susAPIConnectionException """
  pass


class RestAPIException(Exception):
  """
  Exception base for handler exceptions
  """
  pass


class RestClassException(Exception):
  """Broker Exception"""
  pass
