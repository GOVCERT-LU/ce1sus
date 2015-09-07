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
    super(EventsHandler, self).__init__(config)
    self.events_controller = self.controller_factory(EventsController)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def events(self, **args):
    # default settings as not to list to much
    parameters = args.get('parameters')
    count = parameters.get('count', None)
    cache_object = self.get_cache_object(args)
    cache_object.inflated = False
    cache_object.details = False
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

    events, total_events = self.events_controller.get_events(offset, count, cache_object.user, parameters)
    result = list()
    for event in events:
      cache_object.event_permissions = self.permission_controller.get_event_permissions(event, cache_object)
      event = event.attribute_to_dict(event, cache_object)
      if event:
        result.append(event)
    return {'total': total_events, 'data': result}
