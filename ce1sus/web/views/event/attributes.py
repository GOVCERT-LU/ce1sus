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

  def tabs(self):
    return None

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.send_mails = config.get('ce1sus', 'sendmail', False)
    self.attributes_controller = AttributesController(config)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
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
      cb_definitions = self.attributes_controller.get_cb_attr_def_by_obj(obj)
      return self._render_template('/events/event/attributes/attributesModal.html',
                                   event_id=event_id,
                                   object_id=object_id,
                                   attribute=None,
                                   cb_definitions=cb_definitions,
                                   enabled=True)

    except ControllerException as error:
      return self._render_error_page(error)

  def __get_default_share_value(self, attr_definition, obj):
    if attr_definition.share:
      if obj.bit_value.is_shareable:
        default_share_value = 1
      else:
        default_share_value = 0
    else:
      default_share_value = 0
    return default_share_value

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def render_handler_input(self, defattrib_id, event_id, object_id):
    """
    Renders the view for the handler input
    """
    try:
      self._put_to_session('instertedObject', object_id)
      # Clear Session variable
      self._put_to_session('instertAttribute', None)

      event = self.attributes_controller.get_event_by_id(event_id)
      self._is_event_owner(event)
      obj = self.attributes_controller.get_object_by_id(object_id)
      attr_definition = self.attributes_controller.get_attr_def_by_id(defattrib_id)
      default_share_value = self.__get_default_share_value(attr_definition, obj)
      handler = attr_definition.handler
      return handler.render_gui_input(self._render_template,
                                      attr_definition,
                                      default_share_value,
                                      obj.bit_value.is_shareable)
    except (ControllerException, HandlerException) as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def render_handler_view(self, event_id, attribute_id):
    """
    Renders the view for the handler input
    """
    try:
      # Clear Session variable
      self._put_to_session('instertAttribute', None)
      event = self.attributes_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      attribute = self.attributes_controller.get_attribute_by_id(attribute_id)
      user = self._get_user()
      handler = attribute.definition.handler
      return handler.render_gui_view(self._render_template, attribute, user)
    except (ControllerException, HandlerException) as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
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
          attribute = self.attributes_controller.get_attribute_by_id(attribute_id)
      if definition_id:
        definition = self.attributes_controller.get_attr_def_by_id(definition_id)
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
  @cherrypy.tools.allow(methods=['POST'])
  def call_handler_post(self, **kwargs):
    """
    Renders the view for a handling the post by the handler
    """
    try:
      # Clear Session variable
      action = kwargs.get('action')
      event_id = kwargs.pop('event_id', None)
      if not event_id:
        return self._render_error_page('You tried to save an empty page please close and begin anew')
      event = self.attributes_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      obj = self.attributes_controller.get_object_by_id(kwargs.pop('object_id'))
      def_id = kwargs.pop('definition')
      user = self._get_user()
      params = dict()
      for key, value in kwargs.iteritems():
        # note keep everything in utf-8
        params[key] = value.decode('utf-8', 'replace')
      proposal = not (event.creator_group.identifier == user.default_group.identifier)

      attribute, additional_attributes = self.attributes_controller.populate_web_attributes(user,
                                                                                            obj,
                                                                                            def_id,
                                                                                            action,
                                                                                            params,
                                                                                            proposal)

      if action == 'insert':
        attribute, additional_attributes, valid = self.attributes_controller.insert_attributes(user,
                                                                                               obj,
                                                                                               attribute,
                                                                                               additional_attributes)
        if not valid:
          # TODO: activate EDIT
          self._get_logger().info('Attributes are invalid')
          handler = attribute.definition.handler
          return self._return_ajax_post_error(handler.render_gui_edit(self._render_template,
                                                              attribute,
                                                              additional_attributes,
                                                              obj.bit_value.is_shareable))
      if action == 'update':
        # TODO: modify attribute
        attribute, valid = self.attributes_controller.udpate_attributes(user, attribute)

        if not valid:
          return 'Invalid'

      if self.send_mails and (event.creator_group.identifier != user.default_group.identifier):
          self.send_notification_mail(event)

      return self._return_ajax_ok()
    except (ControllerException, HandlerException) as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def view(self, event_id, object_id, attribute_id):
    try:
      event = self.attributes_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      obj = self.attributes_controller.get_object_by_id(object_id)
      cb_definitions = self.attributes_controller.get_cb_attr_def_by_obj(obj)
      attribute = self.attributes_controller.get_attribute_by_id(attribute_id)
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
  @cherrypy.tools.allow(methods=['GET'])
  def edit(self, event_id, object_id, attribute_id):
    try:
      event = self.attributes_controller.get_event_by_id(event_id)
      self._is_event_owner(event)
      attribute = self.attributes_controller.get_attribute_by_id(attribute_id)
      handler = attribute.definition.handler
      additional_attributes = list()
      obj = attribute.object
      handler_content = handler.render_gui_edit(self._render_template,
                                   attribute,
                                   additional_attributes,
                                   obj.bit_value.is_shareable)
      return self._render_template('/events/event/attributes/editAttributesModal.html',
                                   event_id=event_id,
                                   object_id=object_id,
                                   attribute=attribute,
                                   handler_content=handler_content)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def remove_attribute(self, event_id, attribute_id):
    try:
      # Clear Session variable
      self._put_to_session('instertAttribute', None)
      event = self.attributes_controller.get_event_by_id(event_id)
      attribute = self.attributes_controller.get_attribute_by_id(attribute_id)
      self._check_if_allowed_event_object(event, attribute)
      self.attributes_controller.remove_by_id(attribute_id)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._return_ajax_post_error(self._get_error_message(error))

  @require(require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def validate_attribute(self, event_id, attribute_id):
    try:
      self._put_to_session('instertAttribute', None)
      event = self.attributes_controller.get_event_by_id(event_id)
      self._check_if_event_owner(event)
      attribute = self.attributes_controller.get_attribute_by_id(attribute_id)
      self.attributes_controller.validate_attribute(event, attribute, self._get_user())
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._return_ajax_post_error(self._get_error_message(error))
