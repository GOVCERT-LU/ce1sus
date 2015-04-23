# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 14, 2014
"""
from ce1sus.controllers.events.events import EventsController
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventsHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.events_controller = self.controller_factory(EventsController)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def events(self, **args):
    # default settings as not to list to much
    parameters = args.get('parameters')
    count = parameters.get('count', None)
    if count:
      count = int(count)
    else:
      count = None
    page = parameters.get('page', None)
    if page:
      page = int(page)
      if page > 1:
        offset = count * (page - 1)
      else:
        offset = 1
    else:
      offset = None
    details = self.get_detail_value(args)

    events, total_events = self.events_controller.get_events(offset, count, self.get_user(), parameters)
    result = list()
    for event in events:
      result.append(event.to_dict(details, False))
    return {'total': total_events, 'data': result}
