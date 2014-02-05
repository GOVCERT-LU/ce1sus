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
from ce1sus.controllers.admin.subgroups import SubGroupController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException


class AdminSubGroupView(Ce1susBaseView):
  """index view handling all display in the index section"""
  ID = 'Subgroup'

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.subgroup_controller = SubGroupController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    return self._render_template('/admin/common/adminSubItemBase.html',
                                 id=AdminSubGroupView.ID,
                                 url_left_content='/admin/subgroups/left_content')

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def left_content(self):
    """
    renders the left content of the subgroup index page

    :returns: generated HTML
    """
    try:
      subgroups = self.subgroup_controller.get_all_subgroup_definitions()
      return self._render_template('/admin/common/leftContent.html',
                                   id=AdminSubGroupView.ID,
                                   url_right_content='/admin/subgroups/right_content',
                                   items=subgroups)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def right_content(self, subgroup_id):
    """
    renders the right content of the subgroup index page

    :param subgroupid: The subgroup id of the desired displayed subgroup
    :type subgroupid: Integer
    :param subgroup: Similar to the previous subgroup but prevents
                      additional loadings
    :type subgroup: subgroupDefinition

    :returns: generated HTML
    """
    try:
      subgroup = self.subgroup_controller.get_subgroup_definitions_by_id(subgroup_id)
      remaining_subgroups = self.subgroup_controller.get_available_subgroups(subgroup)
      return self._render_template('/admin/subgroups/subgroupRight.html',
                                   id=AdminSubGroupView.ID,
                                   remaining_subgroups=remaining_subgroups,
                                   subgroup=subgroup)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def add_subgroup(self):
    """
    renders the add an subgroup page

    :returns: generated HTML
    """
    return self._render_template('/admin/subgroups/subgroupModal.html',
                                 subgroup=None)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_subgroup_subgroups(self, identifier, operation,
                     existing=None, remaining=None):
    """
    modifies the relation between a subgroup and its subgroups

    :param subgroupID: The subgroupID of the subgroup
    :type subgroupID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the subgroup is not
                            subgroupd to
    :type remainingUsers: Integer array
    :param subgroupUsers: The identifiers of the users which the subgroup is
                       subgroupd to
    :type subgroupUsers: Integer array

    :returns: generated HTML
    """
    try:
      self.subgroup_controller.modify_subgroup_object_relations(operation, identifier, remaining, existing)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def modify_subgroup(self, identifier=None, name=None,
                  description=None, action='insert', share=None):
    """
    modifies or inserts a subgroup with the data of the post

    :param identifier: The identifier of the subgroup,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the subgroup
    :type name: String
    :param description: The description of this subgroup
    :type description: String
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self._get_template('/admin/subgroups/subgroupModal.html')
    try:
      subgroup = self.subgroup_controller.populate_subgroup(identifier,
                                                   name,
                                                   description,
                                                   action,
                                                   share)

      if action == 'insert':
        subgroup, valid = self.subgroup_controller.insert_subgroup_definition(subgroup)
      if action == 'update':
        subgroup, valid = self.subgroup_controller.insert_subgroup_definition(subgroup)
      if action == 'remove':
        subgroup, valid = self.subgroup_controller.insert_subgroup_definition(subgroup)

      if valid:
        return self._return_ajax_ok()
      else:
        return self._render_template('/admin/subgroups/subgroupModal.html',
                                 subgroup=subgroup)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_subgroup(self, subgroupid):
    """
    renders the edit an subgroup page

    :param subgroupid: The subgroup id of the desired displayed subgroup
    :type subgroupid: Integer

    :returns: generated HTML
    """
    try:
      subgroup = self.subgroup_controller.get_subgroup_definitions_by_id(subgroupid)
      return self._render_template('/admin/subgroups/subgroupModal.html',
                                 subgroup=subgroup)
    except ControllerException as error:
      return self._render_error_page(error)
