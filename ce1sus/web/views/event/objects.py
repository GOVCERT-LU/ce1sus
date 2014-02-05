# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 31, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.views.base import Ce1susBaseView
from dagr.web.views.base import SessionNotFoundException
from ce1sus.controllers.event.objects import ObjectsController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException


class ObjectsView(Ce1susBaseView):
  """index view handling all display in the index section"""

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.objects_controller = ObjectsController(config)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def objects(self, event_id, object_id=None):
    """
     renders the file with the base layout of the main object page

    :param object_id: the identifier of the object (only set if the details
                     should be displayed of this object)
    :type object_id: Integer

    :returns: generated HTML
    """
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      # fill dictionary of attribute definitions but only the needed ones

      try:
        if len(event.objects) > 0:
          for obj in event.objects:
            attribute_definitions = self.objects_controller.get_attr_def_by_obj_def(obj.definition)
        else:
          attribute_definitions = dict()
      except ControllerException as error:
        self._get_logger().error(error)
        attribute_definitions = dict()

      ower = self._is_event_owner(event)
      object_list = self.objects_controller.get_all_event_obejcts(event, ower)

      if object_id is None:
        try:
          object_id = self._pull_from_session('instertedObject')
        except SessionNotFoundException:
          object_id = None

      return self._render_template('/events/event/objects/objectsBase.html',
                                   event_id=event_id,
                                   object_list=object_list,
                                   obj_definitions=self.objects_controller.get_cb_object_definitions(),
                                   attribute_definitions=attribute_definitions,
                                   object_id=object_id,
                                   owner=ower)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def add_object(self, event_id):
    """
     renders the file for displaying the add an attribute form

    :returns: generated HTML
    """
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      obj_definitions = self.objects_controller.get_cb_object_definitions()
      return self._render_template('/events/event/objects/objectModal.html',
                                   obj_definitions=obj_definitions,
                                   event_id=event_id,
                                   object=None)

    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def modify_object(self, event_id, definition=None, shared=None, action='insert'):
    """
    Attaches an object to an event

    :param event_id:
    :type event_id: Integer
    :param definition: The identifer of the definition
    :type definition: Integer
    :param shared:
    :type shared:

    :returns: String
    """
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      user = self._get_user()

      obj = self.objects_controller.populate_web_object(None,
                                                        event,
                                                        None,
                                                        definition,
                                                        self._get_user(),
                                                        shared,
                                                        action)
      if action == 'insert':
        obj, valid = self.objects_controller.insert_object(user, event, obj)
      if action == 'remove':
        self.objects_controller.remove_object(user, event, obj)
      if not valid:
          self._get_logger().info('Event is invalid')
          obj_definitions = self.objects_controller.get_cb_object_definitions()
          return self._return_ajax_post_error(self._render_template('/events/event/objects/objectModal.html',
                                                    obj_definitions=obj_definitions,
                                                    event_id=event_id,
                                                    object=obj))
      # save id to session to open the last inserted object
      self._put_to_session('instertedObject', obj.identifier)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def add_child_object(self, event_id, object_id):
    """
    renders the add an object page

    :returns: generated HTML
    """
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)

      obj_definitions = self.objects_controller.get_cb_object_definitions()

      return self._render_template('/events/event/objects/childObjectModal.html',
                                   obj_definitions=obj_definitions,
                                   event_id=event_id,
                                   object_id=object_id,
                                   object=None)
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def attach_child_object(self,
                          object_id=None,
                          event_id=None,
                          definition=None,
                          shared=None):
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      user = self._get_user()
      obj = self.objects_controller.populate_web_object(None,
                                                        event,
                                                        object_id,
                                                        definition,
                                                        self._get_user(),
                                                        shared,
                                                        'insert')
      obj, valid = self.objects_controller.insert_object(user, event, obj)
      if not valid:
          self._get_logger().info('Event is invalid')
          obj_definitions = self.objects_controller.get_cb_object_definitions()
          return self._return_ajax_post_error(self._render_template('/events/event/objects/objectModal.html',
                                                    obj_definitions=obj_definitions,
                                                    event_id=event_id,
                                                    object=obj))
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def set_parent(self, event_id, object_id):
    """
    Renders page for setting the relations between objects,objects and events

    :param identifier: The identifier of the event
    :type identifier: Integer
    :param definition: The identifier of the definition associated to the
                       object
    :type definition: Integer

    :returns: generated HTML
    """
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      obj = self.objects_controller.get_by_id(object_id)

      if obj.event_id:
        is_event_parent = True
        selected = None
      else:
        is_event_parent = False
        selected = obj.parent_object_id

      cb_values = self.objects_controller.get_cb_event_objects(event.identifier, obj.identifier)
      return self._render_template('/events/event/objects/parentModal.html',
                                   object_id=object_id,
                                   event_id=event_id,
                                   cb_values=cb_values,
                                   is_event_parent=is_event_parent,
                                   selected=selected)
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def modify_parent(self,
                    event_id,
                    object_id,
                    parent_object_id=None,
                    set_event_parent=None):
    try:
      if set_event_parent is None and not parent_object_id:
        return self._return_ajax_error('Please select someting before saving.')
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      obj = self.objects_controller.get_by_id(object_id)
      self.objects_controller.set_parent_relation(obj, event, parent_object_id)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def remove_object(self, event_id, object_id):
    """
     renders the file for displaying the add an attribute form

    :returns: generated HTML
    """
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_owner(event)
      user = self._get_user()
      obj = self.objects_controller.get_by_id(object_id)
      self.objects_controller.remove_object(user, event, obj)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def render_properties(self, definition_id, event_id):
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_is_viewable(event)
      definition = self.objects_controller.get_object_definition_by_id(definition_id)
      if definition.share:
        default_share_value = 1
      else:
        default_share_value = 0
      return self._render_template('/events/event/objects/properties.html',
                                   default_share_value=default_share_value)

    except ControllerException as error:
      return self._render_error_page(error)

  @require(require_referer(('/internal')))
  @cherrypy.expose
  def flat_objects(self, event_id):
    try:
      event = self.objects_controller.get_event_by_id(event_id)
      self._check_if_event_owner(event)
      owner = self._is_event_owner(event)
      flat_objects = self.objects_controller.get_flat_objects(event, owner)
      return self._render_template('/events/event/objects/flatview.html',
                                   flat_objects=flat_objects,
                                   event_id=event_id,
                                   owner=owner)
    except ControllerException as error:
      return self._render_error_page(error)
