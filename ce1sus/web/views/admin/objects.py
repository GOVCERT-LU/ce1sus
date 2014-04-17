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
from ce1sus.controllers.admin.objects import ObjectController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException, SpecialControllerException


class AdminObjectsView(Ce1susBaseView):
  """index view handling all display in the index section"""

  ID = 'Object'

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.object_controller = ObjectController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    return self._render_template('/admin/common/adminSubItemBase.html',
                                 id=AdminObjectsView.ID,
                                 url_left_content='/admin/objects/left_content')

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def left_content(self):
    """
    renders the left content of the object index page

    :returns: generated HTML
    """
    try:
      objects = self.object_controller.get_all_object_definitions()
      return self._render_template('/admin/common/leftContent.html',
                                   id=AdminObjectsView.ID,
                                   url_right_content='/admin/objects/right_content',
                                   action_url='/admin/objects/modify_object',
                                   refresh_url='/admin/objects',
                                   modal_content_url='/admin/objects/add_object',
                                   items=objects)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def right_content(self, object_id):
    """
    renders the right content of the object index page

    :param objectid: The object id of the desired displayed object
    :type objectid: Integer
    :param obj: Similar to the previous attribute but prevents
                      additional loadings
    :type obj: ObjectDefinition

    :returns: generated HTML
    """
    try:
      obj = self.object_controller.get_object_definitions_by_id(object_id)
      remaining_attributes = self.object_controller.get_available_attributes(obj)
      return self._render_template('/admin/objects/objectRight.html',
                                   id=AdminObjectsView.ID,
                                   remaining_attributes=remaining_attributes,
                                   object=obj)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def add_object(self):
    """
    renders the add an object page

    :returns: generated HTML
    """
    return self._render_template('/admin/objects/objectModal.html',
                                 object=None)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def edit_object_attributes(self, identifier, operation,
                     existing=None, remaining=None):
    """
    modifies the relation between a object and its attributes

    :param objectID: The objectID of the object
    :type objectID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the object is not
                            attributed to
    :type remainingUsers: Integer array
    :param objectUsers: The identifiers of the users which the object is
                       attributed to
    :type objectUsers: Integer array

    :returns: generated HTML
    """
    try:
      self.object_controller.modify_object_attribute_relations(operation, identifier, remaining, existing)
      return self._return_ajax_ok()
    except SpecialControllerException as error:
      return self._return_ajax_error(error.message)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def modify_object(self, identifier=None, name=None,
                  description=None, action='insert', share=None):
    """
    modifies or inserts a object with the data of the post

    :param identifier: The identifier of the object,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the object
    :type name: String
    :param description: The description of this object
    :type description: String
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """

    try:
      self._check_if_valid_action(action)
      obj = self.object_controller.populate_object(identifier,
                                                   name,
                                                   description,
                                                   action,
                                                   share)

      if action == 'insert':
        obj, valid = self.object_controller.insert_object_definition(obj)
      if action == 'update':
        obj, valid = self.object_controller.update_object_definition(obj)
      if action == 'remove':
        obj, valid = self.object_controller.remove_object_definition(obj)

      if valid:
        return self._return_ajax_ok()
      else:
        return self._return_ajax_post_error(self._render_template('/admin/objects/objectModal.html',
                                 object=obj))
    except SpecialControllerException as error:
      return self._return_ajax_error(error.message)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def edit_object(self, objectid):
    """
    renders the edit an object page

    :param objectid: The object id of the desired displayed object
    :type objectid: Integer

    :returns: generated HTML
    """
    try:
      obj = self.object_controller.get_object_definitions_by_id(objectid)
      return self._render_template('/admin/objects/objectModal.html',
                                 object=obj)
    except ControllerException as error:
      return self._render_error_page(error)
