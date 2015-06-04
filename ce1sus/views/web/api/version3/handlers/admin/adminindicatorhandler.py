# -*- coding: utf-8 -*-

"""
(Description)

Created on Mar 16, 2015
"""
from ce1sus.controllers.events.indicatorcontroller import IndicatorController
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminIndicatorTypesHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.indicator_controller = self.controller_factory(IndicatorController)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def default(self, **args):
    # TODO inmplement indicator handler
    details = self.get_detail_value(args)
    inflated = self.get_inflated_value(args)
    types = self.indicator_controller.get_all_types()
    result = list()
    for type_ in types:
      result.append(type_.to_dict(details, inflated))
    return result
