# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 1, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.views.base import Ce1susBaseView
from ce1sus.controllers.event.attributes import AttributesController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from ce1sus.common.handlers.base import HandlerException
from dagr.controllers.base import ControllerException


class AttributesView(Ce1susBaseView):
  """index view handling all display in the index section"""

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.attributes_controller = AttributesController(config)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def add_attribute(self, event_id, object_id):
    """
     renders the file for adding attributes

    :returns: generated HTML
    """
    try:
      # Clear Session variable
      self._put_to_session('instertAttribute', None)

      event = self.attributes_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      obj = self.attributes_controller.get_object_by_id(object_id)
      cb_definitions = self.attributes_controller.get_cb_attribute_definitions_by_obj(obj)
      return self._render_template('/events/event/attributes/attributesModal.html',
                                   event_id=event_id,
                                   object_id=object_id,
                                   attribute=None,
                                   cb_definitions=cb_definitions,
                                   enabled=True)

    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def render_handler_input(self, defattrib_id, event_id, object_id):
    """
    Renders the view for the handler input
    """
    try:
      # Clear Session variable
      self._put_to_session('instertAttribute', None)

      event = self.attributes_controller.get_event_by_id(event_id)
      self._is_event_owner(event)
      obj = self.attributes_controller.get_object_by_id(object_id)
      attr_definition = self.attributes_controller.get_attribute_definition_by_id(defattrib_id)
      if attr_definition.share:
        if obj.bit_value.is_shareable:
          default_share_value = 1
        else:
          default_share_value = 0
      else:
        default_share_value = 0
      handler = attr_definition.handler
      return handler.render_gui_input(self._render_template,
                                      attr_definition,
                                      default_share_value,
                                      obj.bit_value.is_shareable)
    except (ControllerException, HandlerException) as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def render_handler_view(self, event_id, attribute_id):
    """
    Renders the view for the handler input
    """
    try:
      # Clear Session variable
      self._put_to_session('instertAttribute', None)
      event = self.attributes_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      attribute = self.attributes_controller.get_by_id(attribute_id)
      user = self._get_user()
      handler = attribute.definition.handler
      return handler.render_gui_view(self._render_template, attribute, user)
    except (ControllerException, HandlerException) as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def call_handler_get(self, action, event_id=None, attribute_id=None, definition_id=None):
    """
    Renders the view for and additional handler get handler method
    """
    try:
      # Clear Session variable
      attribute = None
      definition = None
      if event_id:
        event = self.attributes_controller.get_event_by_id(event_id)
        self._check_if_event_is_viewable(event)
        if attribute_id:
          attribute = self.attributes_controller.get_by_id(attribute_id)
      if definition_id:
        definition = self.attributes_controller.get_attribute_definition_by_id(definition_id)
      else:
        if attribute:
          definition = attribute.definition
      if definition:
        user = self._get_user()
        try:
          return definition.handler.render_gui_get(self._render_template, action, attribute, user)
        except HandlerException as error:
          return self._return_ajax_error(self._get_error_message(error))
      else:
        raise ControllerException('Definition cannot be determined as attribute_id is empty and definition_id')
    except (ControllerException, HandlerException) as error:
      return self._render_error_page(error)

  # pylint: disable=C0301
  @require(require_referer(('/internal')))
  @cherrypy.expose
  def call_handler_post(self, **kwargs):
    """
    Renders the view for a handling the post by the handler
    """
    try:
      # Clear Session variable
      event = self.attributes_controller.get_event_by_id(kwargs.pop('event_id'))
      self._check_if_event_is_viewable(event)
      obj = self.attributes_controller.get_object_by_id(kwargs.pop('object_id'))
      action = kwargs.get('action')
      def_id = kwargs.pop('definition')
      user = self._get_user()
      params = dict()
      for key, value in kwargs.iteritems():
        params[key] = value
      attribute, additional_attributes = self.attributes_controller.populate_web_attributes(user,
                                                                                            obj,
                                                                                            def_id,
                                                                                            action,
                                                                                            params)

      if action == 'insert':
        attribute, additional_attributes, valid = self.attributes_controller.insert_attributes(user,
                                                                                               obj,
                                                                                               attribute,
                                                                                               additional_attributes)
        if not valid:
          self._get_logger().info('Attributes are invalid')
          handler = attribute.definition.handler
          return self._return_ajax_post_error(handler.render_gui_edit(self._render_template,
                                                              attribute,
                                                              additional_attributes,
                                                              obj.bit_value.is_shareable))
      if action == 'update':
        # TODO: modify attribute
        pass

      return self._return_ajax_ok()
    except (ControllerException, HandlerException) as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def view(self, event_id, object_id, attribute_id):
    try:
      event = self.attributes_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      obj = self.attributes_controller.get_object_by_id(object_id)
      cb_definitions = self.attributes_controller.get_cb_attribute_definitions_by_obj(obj)
      attribute = self.attributes_controller.get_by_id(attribute_id)
      return self._render_template('/events/event/attributes/attributesModal.html',
                                   event_id=event_id,
                                   object_id=object_id,
                                   attribute=attribute,
                                   cb_definitions=cb_definitions,
                                   enabled=False)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def remove_attribute(self, event_id, attribute_id):
    try:
      # Clear Session variable
      self._put_to_session('instertAttribute', None)

      event = self.attributes_controller.get_event_by_id(event_id)
      self._check_if_event_owner(event)
      self.attributes_controller.remove_by_id(attribute_id)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._return_ajax_post_error(self._get_error_message(error))
