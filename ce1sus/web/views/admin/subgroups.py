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
from ce1sus.web.views.helpers.tabs import AdminTab


class AdminSubGroupView(Ce1susBaseView):
  """index view handling all display in the index section"""

  ID = 'SubGroup'

  def tabs(self):
    subgr_tab = AdminTab(title='SubGroups',
                         url='/admin/subgroups',
                         options='reload',
                         position=4)
    return [subgr_tab]

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.subgroup_controller = SubGroupController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
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
  @cherrypy.tools.allow(methods=['GET'])
  def left_content(self):
    """
    renders the left content of the group index page

    :returns: generated HTML
    """
    try:
      subgroups = self.subgroup_controller.get_all_subgroups()
      return self._render_template('/admin/common/leftContent.html',
                                   id=AdminSubGroupView.ID,
                                   url_right_content='/admin/subgroups/right_content',
                                   action_url='/admin/subgroups/modify_subgroup',
                                   refresh_url='/admin/subgroups',
                                   modal_content_url='/admin/subgroups/add_subgroup',
                                   items=subgroups)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def right_content(self, subgroup_id):
    """
    renders the right content of the group index page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer
    :param group: Similar to the previous group but prevents
                      additional loadings
    :type group: groupDefinition

    :returns: generated HTML
    """

    try:
      subgroup = self.subgroup_controller.get_subgroup_by_id(subgroup_id)
      remaining_subgroups = self.subgroup_controller.get_available_subgroups(subgroup)
      cb_values = self.subgroup_controller.get_cb_tlp_lvls()
      return self._render_template('/admin/subgroups/subgroupRight.html',
                                   id=AdminSubGroupView.ID,
                                   remaining_subgroups=remaining_subgroups,
                                   subgroup=subgroup,
                                   cb_values=cb_values)

    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def add_subgroup(self):
    """
    renders the add an group page

    :returns: generated HTML
    """
    cb_values = self.subgroup_controller.get_cb_tlp_lvls()
    return self._render_template('/admin/subgroups/subgroupModal.html',
                                 subgroup=None,
                                 cb_values=cb_values)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def edit_subgroup_groups(self, identifier, operation,
                           existing=None, remaining=None):
    """
    modifies the relation between a group and its subgroups

    :param groupID: The groupID of the group
    :type groupID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the group is not
                            groupd to
    :type remainingUsers: Integer array
    :param groupUsers: The identifiers of the users which the group is
                       groupd to
    :type groupUsers: Integer array

    :returns: generated HTML
    """
    try:
      self._check_if_valid_operation(operation)
      self.subgroup_controller.modify_subgroup_group_relations(operation, identifier, remaining, existing)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def modify_subgroup(self, identifier=None, name=None,
                      description=None, action='insert'):
    """
    modifies or inserts a group with the data of the post

    :param identifier: The identifier of the group,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the group
    :type name: String
    :param description: The description of this group
    :type description: String
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    try:
      self._check_if_valid_action(action)
      subgroup = self.subgroup_controller.populate_subgroup(identifier,
                                                            name,
                                                            description,
                                                            action)

      if action == 'insert':
        subgroup, valid = self.subgroup_controller.insert_group(subgroup)
      if action == 'update':
        subgroup, valid = self.subgroup_controller.update_group(subgroup)
      if action == 'remove':
        subgroup, valid = self.subgroup_controller.remove_group(subgroup)

      if valid:
        return self._return_ajax_ok()
      else:
        cb_values = self.subgroup_controller.get_cb_tlp_lvls()
        return self._return_ajax_post_error(self._render_template('/admin/subgroups/subgroupModal.html',
                                                                  subgroup=subgroup,
                                                                  cb_values=cb_values))
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def edit_subgroup(self, subgroup_id):
    """
    renders the edit an group page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer

    :returns: generated HTML
    """
    try:
      subgroup = self.subgroup_controller.get_subgroup_by_id(subgroup_id)
      cb_values = self.subgroup_controller.get_cb_tlp_lvls()
      return self._render_template('/admin/subgroups/subgroupModal.html',
                                   subgroup=subgroup,
                                   cb_values=cb_values)
    except ControllerException as error:
      return self._render_error_page(error)
