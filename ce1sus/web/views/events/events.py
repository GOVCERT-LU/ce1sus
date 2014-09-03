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
from ce1sus.web.views.helpers.tabs import MainTab


class EventsView(Ce1susBaseView):
  """events view handling all display in the index section"""

  def tabs(self):
    recent_events_tab = MainTab(title='Recent Events',
                                url='/events/recent',
                                options='reload',
                                position=0)

    unpublished_events = MainTab(title='Unpublished Events',
                                 url='/events/unpublished_events',
                                 options='reload',
                                 position=2)

    unvalidated_proposals = MainTab(title='Unvalidated Proposals',
                                    url='/events/unvalidated_proposals',
                                    options='reload',
                                    position=3)
    return [recent_events_tab, unpublished_events, unvalidated_proposals]

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

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def unpublished_events(self):
    try:
      error = self._pull_from_session('extViewEventError', None)
      if error:
        error = error.message
      ext_event_id = self._pull_from_session('extViewEvent', None)

      user = self._get_user()
      events = self.events_controller.get_unpublished_user_events(user)
      return self._render_template('/events/unpublished.html',
                                   events=events,
                                   url='/events/event/view',
                                   tab_id='eventsTabTabContent',
                                   error=error,
                                   ext_event_id=ext_event_id)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def unvalidated_proposals(self):
    try:
      error = self._pull_from_session('extViewEventError', None)
      if error:
        error = error.message
      ext_event_id = self._pull_from_session('extViewEvent', None)

      user = self._get_user()
      events = self.events_controller.get_unvalidated_user_events(user)
      return self._render_template('/events/unvalidated.html',
                                   events=events,
                                   url='/events/event/view',
                                   tab_id='eventsTabTabContent',
                                   error=error,
                                   ext_event_id=ext_event_id)
    except ControllerException as error:
      return self._render_error_page(error)
