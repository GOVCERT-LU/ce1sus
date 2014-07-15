# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.views.base import Ce1susBaseView
from ce1sus.controllers.events.events import EventsController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException


class EventsView(Ce1susBaseView):
  """events view handling all display in the index section"""

  def tabs(self):
    """Should return [('name', lvl, 'url', ['close'|'reload'|None])] or None"""
    return [('Recent Events', 0, '/events/recent', 'reload')]

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.events_controller = EventsController(config)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    """
    renders the events page

    :returns: generated HTML
    """
    self.set_admin_area(False)
    if self.view_handler:
      main_tabs = self.view_handler.main_tabs
    else:
      main_tabs = list()
    return self._render_template('/events/eventsBase.html',
                                 main_tabs=main_tabs)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def recent(self, limit=200, offset=0):
    """
    Renders the event Page (list of all events)

    :returns: generated HTML
    """

    try:
      error = self._pull_from_session('extViewEventError', None)
      if error:
        error = error.message
      ext_event_id = self._pull_from_session('extViewEvent', None)

      user = self._get_user()
      events = self.events_controller.get_user_events(user, limit, offset)
      return self._render_template('/events/recent.html',
                                   events=events,
                                   url='/events/event/view',
                                   tab_id='eventsTabTabContent',
                                   error=error,
                                   ext_event_id=ext_event_id)
    except ControllerException as error:
      return self._render_error_page(error)
