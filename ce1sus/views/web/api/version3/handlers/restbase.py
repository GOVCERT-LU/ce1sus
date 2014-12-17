# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 5, 2014
"""

import cherrypy

from ce1sus.views.web.common.base import BaseView
from ce1sus.views.web.common.decorators import SESSION_USER


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

ALLOWED_HTTP_METHODS = ['GET', 'PUT', 'POST', 'DELETE']


def rest_method(**kwargs):

  default = kwargs.get('default', False)

  # TODO: check if the method has the right amount of arguments and the right ones
  def decorate(method):
    method.rest_method = True
    method.default_fct = default
    return method

  return decorate


def methods(**kwargs):
  # TODO: check if the method has the right amount of arguments and the right ones
  allowed = kwargs.get('allowed', list())

  def decorate(method):

    if not isinstance(allowed, list):
      raise RestHandlerException(u'Allowed methods for function {0} has to be an array'.format(method.__name__))
    else:
      method.allowed_http_methods = allowed
    return method

  return decorate


def require(*conditions):

  def decorate(method):
    method.require_auth_flag = True
    method.require_auth = list()
    if conditions:
      method.require_auth.extend(conditions)
    return method

  return decorate


class RestHandlerException(Exception):
  """
  Exception base for handler exceptions
  """
  pass


class RestHandlerNotFoundException(RestHandlerException):
  """
  Exception base for handler exceptions
  """
  pass


class RestBaseHandler(BaseView):
  """Base class for handlers"""

  def __init__(self, config):
    BaseView.__init__(self, config)

  @property
  def name(self):
    return self.__class__.__name__

  def get_detail_value(self, args):
    parameters = args.get('parameters')
    details = parameters.get('complete', 'false')
    if details == 'true':
      details = True
    else:
      details = False
    return details

  def get_inflated_value(self, args):
    parameters = args.get('parameters')
    inflated = parameters.get('inflated', 'false')
    if inflated == 'true':
      inflated = True
    else:
      inflated = False
    return inflated
