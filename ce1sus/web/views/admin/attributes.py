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
from ce1sus.controllers.admin.attributes import AttributeController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException, SpecialControllerException


class AdminAttributeView(Ce1susBaseView):
  """index view handling all display in the index section"""

  ID = 'Attribute'

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.attribute_controller = AttributeController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    return self._render_template('/admin/common/adminSubItemBase.html',
                                 id=AdminAttributeView.ID,
                                 url_left_content='/admin/attributes/left_content')

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def left_content(self):
    """
    renders the left content of the attribute index page

    :returns: generated HTML
    """
    try:
      attributes = self.attribute_controller.get_all_attribute_definitions()
      return self._render_template('/admin/common/leftContent.html',
                                   id=AdminAttributeView.ID,
                                   url_right_content='/admin/attributes/right_content',
                                   action_url='/admin/attributes/modify_object',
                                   refresh_url='/admin/attributes',
                                   modal_content_url='/admin/attributes/add_object',
                                   items=attributes)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def right_content(self, attribute_id):
    """
    renders the right content of the attribute index page

    :param attributeid: The attribute id of the desired displayed attribute
    :type attributeid: Integer
    :param attribute: Similar to the previous attribute but prevents
                      additional loadings
    :type attribute: attributeDefinition

    :returns: generated HTML
    """
    try:
      attribute = self.attribute_controller.get_attribute_definitions_by_id(attribute_id)
      remaining_objects = self.attribute_controller.get_available_objects(attribute)
      cb_values = self.attribute_controller.get_cb_table_definitions()
      cb_handler_values = self.attribute_controller.get_cb_handler_definitions()
      return self._render_template('/admin/attributes/attributeRight.html',
                                   id=AdminAttributeView.ID,
                                   remaining_objects=remaining_objects,
                                   attribute=attribute,
                                   cb_values=cb_values,
                                   cb_handler_values=cb_handler_values)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def add_attribute(self):
    """
    renders the add an attribute page

    :returns: generated HTML
    """
    cb_values = self.attribute_controller.get_cb_table_definitions()
    cb_handler_values = self.attribute_controller.get_cb_handler_definitions()
    return self._render_template('/admin/attributes/attributeModal.html',
                                 attribute=None,
                                 cb_values=cb_values,
                                 cb_handler_values=cb_handler_values)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_attribute_attributes(self, identifier, operation,
                     existing=None, remaining=None):
    """
    modifies the relation between a attribute and its attributes

    :param attributeID: The attributeID of the attribute
    :type attributeID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the attribute is not
                            attributed to
    :type remainingUsers: Integer array
    :param attributeUsers: The identifiers of the users which the attribute is
                       attributed to
    :type attributeUsers: Integer array

    :returns: generated HTML
    """
    try:
      self.attribute_controller.modify_object_attribute_relations(operation, identifier, remaining, existing)
      return self._return_ajax_ok()
    except SpecialControllerException as error:
      return self._return_ajax_error(error.message)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def modify_attribute(self, identifier=None, name=None, description='',
                      regex='^.*$', class_index=0, action='insert',
                      handler_index=0, share=None, relation=None):
    """
    modifies or inserts a attribute with the data of the post

    :param identifier: The identifier of the attribute,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the attribute
    :type name: String
    :param description: The description of this attribute
    :type description: String
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self._get_template('/admin/attributes/attributeModal.html')
    try:
      attribute = self.attribute_controller.populate_object(identifier,
                                                              name,
                                                              description,
                                                              regex,
                                                              class_index,
                                                              action,
                                                              handler_index,
                                                              share,
                                                              relation)

      if action == 'insert':
        attribute, valid = self.attribute_controller.insert_attribute_definition(attribute)
      if action == 'update':
        attribute, valid = self.attribute_controller.update_attribtue_definition(attribute)
      if action == 'remove':
        attribute, valid = self.attribute_controller.remove_attribute_definition(attribute)

      if valid:
        return self._return_ajax_ok()
      else:
        return self._render_template('/admin/attributes/attributeModal.html',
                                 attribute=attribute)
    except SpecialControllerException as error:
      return self._return_ajax_error(error.message)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_attribute(self, attributeid):
    """
    renders the edit an attribute page

    :param attributeid: The attribute id of the desired displayed attribute
    :type attributeid: Integer

    :returns: generated HTML
    """
    try:
      attribute = self.attribute_controller.get_attribute_definitions_by_id(attributeid)
      cb_values = self.attribute_controller.get_cb_table_definitions()
      cb_handler_values = self.attribute_controller.get_cb_handler_definitions()
      return self._render_template('/admin/attributes/attributeModal.html',
                                   attribute=attribute,
                                   cb_values=cb_values,
                                   cb_handler_values=cb_handler_values)
    except ControllerException as error:
      return self._render_error_page(error)
