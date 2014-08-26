# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 3, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.views.base import Ce1susBaseView, privileged
from ce1sus.controllers.admin.validation import ValidationController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from dagr.helpers.datumzait import DatumZait
from ce1sus.web.views.helpers.tabs import AdminTab, ValidationTab


class AdminValidationView(Ce1susBaseView):
  """index view handling all display in the index section"""

  def tabs(self):
    val_tab = AdminTab(title='Validation',
                       url='/admin/validation',
                       options='reload',
                       position=0)
    overview_tab = ValidationTab(title='Overview',
                                 url='/admin/validation/event_details',
                                 options='reload',
                                 position=0)
    strobj_tab = ValidationTab(title='Structured Objects',
                               url='/admin/validation/event_objects',
                               options='reload',
                               position=1)
    flat_obj_tab = ValidationTab(title='Flat Objects',
                                 url='/admin/validation/flat_event_objects',
                                 options='reload',
                                 position=2)
    rel_tab = ValidationTab(title='Relations',
                            url='/events/event/relations',
                            options='reload',
                            position=3)
    groups_tab = ValidationTab(title='Groups',
                               url='/events/event/groups/groups',
                               options='reload',
                               position=4)
    return [val_tab, overview_tab, strobj_tab, flat_obj_tab, rel_tab, groups_tab]

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.validation_controller = ValidationController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    return self._render_template('/admin/validation/validationBase.html')

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def unvalidated(self):
    try:
      events = self.validation_controller.get_all_unvalidated_events()
      return self._render_template('/events/recent.html',
                                   events=events,
                                   url='/admin/validation/event',
                                   tab_id='validationTabsTabContent',
                                   error=None,
                                   ext_event_id=None)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def event(self, event_id):
    """
    renders the base page for displaying events

    :returns: generated HTML
    """
    if self.view_handler:
      tabs = self.view_handler.validation_tabs
    else:
      tabs = list()
    return self._render_template('/admin/validation/eventValBase.html',
                                 event_id=event_id,
                                 tabs=tabs)

  def __render_event_details(self, template_name, event):
    """
    renders the template

    :param template_name: file string of the template
    :type template_name: String
    :param event:
    :type event: Event

    :returns: generated HTML
    """

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def event_details(self, event_id):
    """
    renders the event page for displaying a single event

    :returns: generated HTML
    """
    try:
      event = self.validation_controller.get_event_by_id(event_id)
      relations = self.validation_controller.get_related_events(event)
      return self._render_template('/admin/validation/eventDetails.html',
                                   event=event,
                                   today=DatumZait.utcnow(),
                                   status_values=Status.get_definitions(),
                                   tlp_values=TLPLevel.get_definitions(),
                                   analysis_values=Analysis.get_definitions(),
                                   risk_values=Risk.get_definitions(),
                                   relations=relations)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def event_objects(self, eventid):
    try:
      event = self.validation_controller.get_event_by_id(eventid)
      self._check_if_event_is_viewable(event)

      return self._render_template('/events/event/objects/objectsBase.html',
                                   event_id=eventid,
                                   object_list=event.objects,
                                   obj_definitions=dict(),
                                   attribute_definitions=dict(),
                                   object_id=None,
                                   owner=True,
                                   user=self._get_user())
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def flat_event_objects(self, event_id):
    try:
      event = self.validation_controller.get_event_by_id(event_id)

      flat_objects = self.validation_controller.get_flat_objects(event)
      return self._render_template('/events/event/objects/flatview.html',
                                   flat_objects=flat_objects,
                                   event_id=event_id,
                                   owner=True,
                                   user=self._get_user())
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def validate_event(self, event_id):
    try:
      event = self.validation_controller.get_event_by_id(event_id)
      user = self._get_user()
      self.validation_controller.validate_event(event, user)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def delete_unvalidated_event(self, event_id):
    try:
      event = self.validation_controller.get_event_by_id(event_id)
      self.validation_controller.remove_unvalidated_event(event)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)
