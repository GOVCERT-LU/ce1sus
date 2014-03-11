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

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.events_controller = EventsController(config)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the events page

    :returns: generated HTML
    """
    self.set_admin_area(False)
    return self._render_template('/events/eventsBase.html')

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def recent(self, limit=200, offset=0):
    """
    Renders the event Page (list of all events)

    :returns: generated HTML
    """

    try:
      error = self._get_from_session('extViewEventError', None)
      if error:
        error = error.message
      ext_event_id = self._get_from_session('extViewEvent', None)
      if ext_event_id:
        self._put_to_session('extViewEvent', None)

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
