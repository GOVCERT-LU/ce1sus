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
from ce1sus.controllers.admin.groups import GroupsController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException


class AdminUserView(Ce1susBaseView):
  """index view handling all display in the index section"""

  ID = 'User'

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.user_controller = UserController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    index page of the administration section

    :returns: generated HTML
    """
    return self._render_template('/admin/common/adminSubItemBase.html',
                                 id=AdminUserView.ID,
                                 url_left_content='/admin/users/left_content')

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def left_content(self):
    """
    renders the left content of the user index page

    :returns: generated HTML
    """
    try:
      users = self.user_controller.get_all_user_definitions()
      return self._render_template('/admin/common/leftContent.html',
                                   id=AdminUserView.ID,
                                   url_right_content='/admin/users/right_content',
                                   items=users)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def right_content(self, user_id):
    """
    renders the right content of the user index page

    :param userid: The user id of the desired displayed user
    :type userid: Integer
    :param user: Similar to the previous user but prevents
                      additional loadings
    :type user: userDefinition

    :returns: generated HTML
    """
    try:
      user = self.user_controller.get_user_definitions_by_id(user_id)
      remaining_users = self.user_controller.get_available_users(user)
      return self._render_template('/admin/users/userRight.html',
                                   id=AdminUserView.ID,
                                   remaining_users=remaining_users,
                                   user=user)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def add_user(self):
    """
    renders the add an user page

    :returns: generated HTML
    """
    return self._render_template('/admin/users/userModal.html',
                                 user=None)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_user_users(self, identifier, operation,
                     existing=None, remaining=None):
    """
    modifies the relation between a user and its users

    :param userID: The userID of the user
    :type userID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the user is not
                            userd to
    :type remainingUsers: Integer array
    :param userUsers: The identifiers of the users which the user is
                       userd to
    :type userUsers: Integer array

    :returns: generated HTML
    """
    try:
      self.user_controller.modify_user_object_relations(operation, identifier, remaining, existing)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def modify_user(self, identifier=None, name=None,
                  description=None, action='insert', share=None):
    """
    modifies or inserts a user with the data of the post

    :param identifier: The identifier of the user,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the user
    :type name: String
    :param description: The description of this user
    :type description: String
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self._get_template('/admin/users/userModal.html')
    try:
      user = self.user_controller.populate_user(identifier,
                                                   name,
                                                   description,
                                                   action,
                                                   share)

      if action == 'insert':
        user, valid = self.user_controller.insert_user_definition(user)
      if action == 'update':
        user, valid = self.user_controller.insert_user_definition(user)
      if action == 'remove':
        user, valid = self.user_controller.insert_user_definition(user)

      if valid:
        return self._return_ajax_ok()
      else:
        return self._render_template('/admin/users/userModal.html',
                                 user=user)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_user(self, userid):
    """
    renders the edit an user page

    :param userid: The user id of the desired displayed user
    :type userid: Integer

    :returns: generated HTML
    """
    try:
      user = self.user_controller.get_user_definitions_by_id(userid)
      return self._render_template('/admin/users/userModal.html',
                                 user=user)
    except ControllerException as error:
      return self._render_error_page(error)
