# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 24, 2014
"""
from ce1sus.helpers.common.objects import get_class


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def create_response(obj):
  result = dict()
  if isinstance(obj, Exception):
    result['error'] = dict()
    result['error']['type'] = 'danger'
    result['error']['classname'] = obj.__class__.__name__
    result['error']['message'] = '{0}'.format(obj.message)
    result['data'] = None
  else:
    result['error'] = None
    result['data'] = obj
  return result