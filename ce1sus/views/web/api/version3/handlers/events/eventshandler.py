# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 14, 2014
"""
from ce1sus.controllers.events.events import EventsController
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventsHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.events_controller = EventsController(config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  def events(self, **args):
    # default settings as not to list to much
    parameters = args.get('parameters')
    count = parameters.get('count', 10)
    page = parameters.get('page', 1)
    details = args.get('headers').get('Complete', 'false')
    if details == 'true':
      details = True
    else:
      details = False
    events, total_events = self.events_controller.get_events(page, count, self.get_user())
    result = list()
    for event in events:
      result.append(event.to_dict(details))
    return {'total': total_events, 'data': result}
