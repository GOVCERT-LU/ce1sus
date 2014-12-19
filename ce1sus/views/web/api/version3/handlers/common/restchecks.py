# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 19, 2014
"""
from ce1sus.common.checks import is_user_priviledged
from ce1sus.controllers.base import ControllerException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ChecksHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def checks(self, **args):
    try:
      raise RestHandlerException('No checks selected')
    except ControllerException as error:
      raise RestHandlerException(error)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  def isuseradmin(self, **args):
    return is_user_priviledged(self.get_user())
