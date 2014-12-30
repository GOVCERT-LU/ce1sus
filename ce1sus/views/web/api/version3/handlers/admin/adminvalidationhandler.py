# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 29, 2014
"""
from ce1sus.controllers.events.events import EventsController
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require
from ce1sus.views.web.common.decorators import privileged, validate


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ValidationHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.events_controller = EventsController(config)

  @rest_method()
  @methods(allowed=['GET'])
  @require(privileged(), validate())
  def unvalidated(self, **args):
    # default settings as not to list to much
    parameters = args.get('parameters')
    count = parameters.get('count', 10)
    page = parameters.get('page', 1)
    details = self.get_detail_value(args)
    events, total_events = self.events_controller.get_unvalidated_events(page, count, self.get_user())
    result = list()
    for event in events:
      result.append(event.to_dict(details, False))
    return {'total': total_events, 'data': result}
