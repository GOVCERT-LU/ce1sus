# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from ce1sus.web.rest.handlers.restbase import RestBaseHandler
from ce1sus.controllers.events.events import EventsController
from dagr.helpers.datumzait import DatumZait
from dagr.controllers.base import ControllerException


class RestEventsHandler(RestBaseHandler):

  MAX_LIMIT = 20

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.events_controller = EventsController(config)

  def view(self, uuid, **options):
    try:
      uuids = options.get('uuids', list())
      with_definition = options.get('fulldefinitions', False)
      start_date = options.get('startdate', None)
      end_date = options.get('enddate', DatumZait.utcnow())
      offset = options.get('page', 0)
      limit = options.get('limit', 20)

      # limit has to be between 0 and maximum value
      if limit < 0 or limit > RestEventsHandler.MAX_LIMIT:
        self._raise_error('InvalidArgument',
                          msg='The limit value has to be between 0 and 20')

      # search only if something was specified
      if start_date or uuids:
        events = self.events_controller.get_events(uuids,
                                                   start_date,
                                                   end_date,
                                                   offset,
                                                   limit,
                                                   self._get_user(False))
      else:
        events = self.events_controller.get_user_events(user=self._get_user(False),
                                                        limit=limit,
                                                        offset=offset)

      result = list()
      for event in events:
        try:
          viewable = self._is_event_viewable(event)
          owner = self._is_event_owner(event)
          if viewable or owner:
            result.append(self.create_rest_obj(event, self._get_user(False), True, with_definition))
        except cherrypy.HTTPError:
          pass

      result = {'Results': result}
      return self.create_return_msg(result)

    except ControllerException as error:
      return self._raise_error('ControllerException', error)

  # pylint: disable=R0201
  def get_function_name(self, parameter, action):
    return None
