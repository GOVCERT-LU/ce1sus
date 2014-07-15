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
from ce1sus.controllers.event.event import EventController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from dagr.helpers.datumzait import DatumZait
from dagr.controllers.base import ControllerException
from cherrypy import HTTPRedirect
from ce1sus.web.views.helpers.tabs import MainTab, EventTab


class EventView(Ce1susBaseView):
  """index view handling all display in the index section"""

  def tabs(self):
    add_event_tab = MainTab(title='Add Event',
                                url='/events/event/add_event',
                                options=None,
                                position=2)
    overview_tab = EventTab(title='Overview',
                                url='/events/event/event',
                                options='reload',
                                position=0)
    relations_tab = EventTab(title='Relations',
                                url='/events/event/relations',
                                options='reload',
                                position=3)
    return [add_event_tab, overview_tab, relations_tab]

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.event_controller = EventController(config)

  def __render_event_details(self, template_name, event):
    """
    renders the template

    :param template_name: file string of the template
    :type template_name: String
    :param event:
    :type event: Event

    :returns: generated HTML
    """
    return self._render_template(template_name,
                                 event=event,
                                 today=DatumZait.utcnow(),
                                 status_values=Status.get_definitions(),
                                 tlp_values=TLPLevel.get_definitions(),
                                 analysis_values=Analysis.get_definitions(),
                                 risk_values=Risk.get_definitions(),
                                 owner=self._is_event_owner(event))

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def event(self, event_id):
    """
    renders the event page for displaying a single event

    :returns: generated HTML
    """
    # relations table
    user = self._get_user()
    cache = self._get_authorized_events_cache()
    try:
      event = self.event_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      relations = self.event_controller.get_related_events(event, user, cache)
      return self._render_template('/events/event/overview.html',
                                   event=event,
                                   owner=self._is_event_owner(event),
                                   relations=relations,
                                   status_values=Status.get_definitions(),
                                   tlp_values=TLPLevel.get_definitions(),
                                   analysis_values=Analysis.get_definitions(),
                                   risk_values=Risk.get_definitions())
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def view(self, event_id):
    """
    renders the base page for displaying events

    :returns: generated HTML
    """
    try:
      event = self.event_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      tabs = list()
      if self.view_handler:
        tabs = self.view_handler.event_tabs
      return self._render_template('/events/event/eventBase.html',
                                   event_id=event_id,
                                   owner=self._is_event_owner(event),
                                   tabs=tabs)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def edit_event(self, event_id):
    """
    renders the base page for editing a single event

    :returns: generated HTML
    """
    # right checks
    try:
      event = self.event_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      return self.__render_event_details('/events/event/editDetails.html', event)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def modify_event(self, **kwargs):
    """
    modifies or inserts an event with the data of the post

    :param identifier: The identifier of the event,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String
    :param status: The identifier of the statuts
    :type status: Integer
    :param tlp_index: The identifier of the TLP level
    :type tlp_index: Integer
    :param description: The desc
    :type description: String
    :param email: The email of the user
    :type email: String

    :returns: generated HTML
    """
    try:
      user = self._get_user()
      action = kwargs.get('action', None)
      self._check_if_valid_action(action)
      event = self.event_controller.populate_web_event(user, **kwargs)
      if action == 'insert':
        event, valid = self.event_controller.insert_event(user, event)
        if not valid:
          self._get_logger().info('Event is invalid')
          return self._return_ajax_post_error(self.__render_event_details('/events/event/addEvent.html',
                                                          event))
      if action == 'remove':
        self._check_if_event_owner(event)
        self.event_controller.remove_event(user, event)

      if action == 'update':
        self._check_if_event_owner(event)
        event, valid = self.event_controller.update_event(user, event)
        if not valid:
          self._get_logger().info('Event is invalid')
          return self._return_ajax_post_error(self.__render_event_details('/events/event/editDetails.html',
                                                            event))
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def add_event(self):
    """
    Renders the page for adding an event

    :param event: Is not null in case of an erroneous input
    :type event: Event

    :returns: generated HTML
    """
    return self.__render_event_details('/events/event/addEvent.html', None)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def relations(self, event_id):
    """
    Renders the relation page of an event

    :param event_id: Identifier of the event
    :type event_id: Integer

    :returns: generated HTML
    """
    try:
      event = self.event_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      user = self._get_user()
      cache = self._get_authorized_events_cache()
      relations = self.event_controller.get_full_event_relations(event, user, cache)
      return self._render_template('/events/event/relations.html',
                                   event=event,
                                   relations=relations)
    except ControllerException as error:
      self._get_logger().error(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def extview(self, uuid):
    try:
      event = self.event_controller.get_by_uuid(uuid)
      self._check_if_event_is_viewable(event)
      self._put_to_session('extViewEvent', event.identifier)
      raise HTTPRedirect('/internal')
    except ControllerException as error:
      self._get_logger().error(error)
      self._put_to_session('extViewEventError', error)
      raise HTTPRedirect('/internal')
