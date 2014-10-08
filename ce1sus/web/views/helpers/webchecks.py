# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 8, 2014
"""


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import ce1sus.common.checks as checks


def is_allowed(context, event, user):
  return checks.is_allowed(event, user)


def is_attribute_owner(context, attribute, user):
  return checks.is_attribtue_owner(attribute, user)


def is_attribute_viewable(context, event, attribute, user):
  return checks.is_attribute_viewable(event, attribute, user)
