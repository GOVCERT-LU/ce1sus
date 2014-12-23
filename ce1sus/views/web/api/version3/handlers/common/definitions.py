# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 19, 2014
"""
from ce1sus.controllers.base import ControllerException
from ce1sus.db.classes.common import Status, Analysis, Risk, TLP
from ce1sus.mappers.stix.helpers.common import relation_definitions
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


class RelationHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def relations(self, **args):
    try:
      relations_dict = relation_definitions()
      # prepare for output
      result = list()
      for name, description in relations_dict.iteritems():
        result.append({'name': name, 'description': description})
      return result
    except ControllerException as error:
      raise RestHandlerException(error)
