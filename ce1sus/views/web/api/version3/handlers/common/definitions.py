# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 19, 2014
"""
from ce1sus.controllers.base import ControllerException
from ce1sus.db.classes.common import Status, Analysis, Risk, TLP
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class StatusHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def statuses(self, **args):
    try:
      return Status.get_cb_values()
    except ControllerException as error:
      raise RestHandlerException(error)


class AnalysisHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def analyses(self, **args):
    try:
      return Analysis.get_cb_values()
    except ControllerException as error:
      raise RestHandlerException(error)


class RiskHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def risks(self, **args):
    try:
      return Risk.get_cb_values()
    except ControllerException as error:
      raise RestHandlerException(error)


class TLPHanlder(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def tlps(self, **args):
    try:
      return TLP.get_cb_values()
    except ControllerException as error:
      raise RestHandlerException(error)
