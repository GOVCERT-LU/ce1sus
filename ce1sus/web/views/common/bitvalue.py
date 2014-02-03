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
from ce1sus.controllers.event.bitvalue import BitValueController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException


class BitValueView(Ce1susBaseView):
  """index view handling all display in the index section"""

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.bit_value_controller = BitValueController(config)

  def __generate_template(self, event_id, instance, parentDisabled):
    return self._render_template('/events/event/bitvalue/bitvalueModal.html',
                           identifier=instance.identifier,
                           bit_value=instance.bit_value,
                           event_id=event_id,
                           enabled=parentDisabled)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def set_object_properties(self, event_id, object_id):
    try:
      event = self.bit_value_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      obj = self.bit_value_controller.get_object_by_id(object_id)
      return self.__generate_template(event_id, obj, True)
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def modify_object_properties(self, event_id, identifier, shared):
    try:
      event = self.bit_value_controller.get_event_by_id(event_id)
      self._check_if_event_owner(event)
      user = self._get_user()
      self.bit_value_controller.set_object_values(user, event, identifier, shared)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def set_attribute_properties(self, event_id, object_id, attribute_id):
    try:
      event = self.bit_value_controller.get_event_by_id(event_id)
      self._check_if_event_owner(event)
      obj = self.bit_value_controller.get_object_by_id(object_id)
      attribute = self.bit_value_controller.get_attribute_by_id(attribute_id)
      return self.__generate_template(event_id, attribute, obj.bit_value.is_shareable)
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def modify_attribute_properties(self, event_id, identifier, shared):
    try:
      event = self.bit_value_controller.get_event_by_id(event_id)
      self._check_if_event_owner(event)
      user = self._get_user()
      self.bit_value_controller.set_attribute_values(user, event, identifier, shared)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)
