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
from ce1sus.controllers.admin.groups import GroupController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException
from ce1sus.web.views.helpers.tabs import AdminTab


class AdminGroupView(Ce1susBaseView):
  """index view handling all display in the index section"""

  ID = 'Group'

  def tabs(self):
    group_tab = AdminTab(title='Groups',
                         url='/admin/groups',
                         options='reload',
                         position=0)
    return [group_tab]

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.group_controller = GroupController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    return self._render_template('/admin/common/adminSubItemBase.html',
                                 id=AdminGroupView.ID,
                                 url_left_content='/admin/groups/left_content')

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def left_content(self):
    """
    renders the left content of the group index page

    :returns: generated HTML
    """
    try:
      groups = self.group_controller.get_all_groups()
      return self._render_template('/admin/common/leftContent.html',
                                   id=AdminGroupView.ID,
                                   url_right_content='/admin/groups/right_content',
                                   action_url='/admin/groups/modify_group',
                                   refresh_url='/admin/groups',
                                   modal_content_url='/admin/groups/add_group',
                                   items=groups)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def right_content(self, group_id):
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
      group = self.group_controller.get_group_by_id(group_id)
      remaining_groups = self.group_controller.get_available_subgroups(group)
      cb_values = self.group_controller.get_cb_tlp_lvls()
      return self._render_template('/admin/groups/groupRight.html',
                                   id=AdminGroupView.ID,
                                   remaining_groups=remaining_groups,
                                   group=group,
                                   cb_values=cb_values)

    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def add_group(self):
    """
    renders the add an group page

    :returns: generated HTML
    """
    cb_values = self.group_controller.get_cb_tlp_lvls()
    return self._render_template('/admin/groups/groupModal.html',
                                 group=None,
                                 cb_values=cb_values)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def edit_group_subgroups(self, identifier, operation,
                           existing=None, remaining=None):
    """
    modifies the relation between a group and its groups

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
      self.group_controller.modify_group_subgroup_relations(operation, identifier, remaining, existing)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def modify_group(self, identifier=None, name=None,
                   description=None, download=None, action='insert',
                   tlp_lvl=None, email=None, usermails=None, gpgkey=None):
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
      group = self.group_controller.populate_group(identifier,
                                                   name,
                                                   description,
                                                   download,
                                                   action,
                                                   tlp_lvl,
                                                   email,
                                                   gpgkey,
                                                   usermails)

      if action == 'insert':
        group, valid = self.group_controller.insert_group(group)
      if action == 'update':
        group, valid = self.group_controller.update_group(group)
      if action == 'remove':
        group, valid = self.group_controller.remove_group(group)

      if valid:
        return self._return_ajax_ok()
      else:
        cb_values = self.group_controller.get_cb_tlp_lvls()
        return self._return_ajax_post_error(self._render_template('/admin/groups/groupModal.html',
                                                                  group=group,
                                                                  cb_values=cb_values))
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def edit_group(self, group_id):
    """
    renders the edit an group page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer

    :returns: generated HTML
    """
    try:
      group = self.group_controller.get_group_by_id(group_id)
      cb_values = self.group_controller.get_cb_tlp_lvls()
      return self._render_template('/admin/groups/groupModal.html',
                                   group=group,
                                   cb_values=cb_values)
    except ControllerException as error:
      return self._render_error_page(error)
