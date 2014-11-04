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
    result['status'] = dict()
    result['status']['type'] = 'danger'
    result['status']['classname'] = obj.__class__.__name__
    result['status']['message'] = '{0}'.format(obj.message)
    result['data'] = None
  else:
    result['status'] = dict()
    result['status']['type'] = 'success'
    result['data'] = obj
  return result
