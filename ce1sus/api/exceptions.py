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
  pass


class Ce1susForbiddenException(Ce1susAPIException):
  pass


class Ce1susNothingFoundException(Ce1susAPIException):
  pass


class Ce1susUndefinedException(Ce1susAPIException):
  pass


class Ce1susUnkownDefinition(Ce1susAPIException):
  pass


class Ce1susInvalidParameter(Ce1susAPIException):
  pass


class Ce1susAPIConnectionException(Ce1susAPIException):
  pass
