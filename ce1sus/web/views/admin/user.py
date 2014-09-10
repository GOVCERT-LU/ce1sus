# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 3, 2014
"""
from ce1sus.controllers.login import LoginController

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.views.base import Ce1susBaseView, privileged
from ce1sus.controllers.admin.user import UserController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException
from ce1sus.web.views.helpers.tabs import AdminTab


class AdminUserView(Ce1susBaseView):
  """index view handling all display in the index section"""

  ID = 'User'

  def tabs(self):
    usr_tab = AdminTab(title='Users',
                       url='/admin/users',
                       options='reload',
                       position=0)
    return [usr_tab]

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.user_controller = UserController(config)
    self.login_controller = LoginController(config)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
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
  @cherrypy.tools.allow(methods=['GET'])
  def left_content(self):
    """
    renders the left content of the user index page

    :returns: generated HTML
    """
    try:
      users = self.user_controller.get_all_users()
      return self._render_template('/admin/users/leftContent.html',
                                   items=users,
                                   use_ldap=self.user_controller.use_ldap,
                                   enabled=True)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
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
      user = self.user_controller.get_user_by_id(user_id)
      cb_values = self.user_controller.get_cb_group_values()
      return self._render_template('/admin/users/userRight.html',
                                   id=AdminUserView.ID,
                                   cb_values=cb_values,
                                   user=user)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def add_user(self):
    """
    renders the add an user page

    :returns: generated HTML
    """
    try:
      cb_values = self.user_controller.get_cb_group_values()
      return self._render_template('/admin/users/userModal.html',
                                   cb_values=cb_values,
                                   user=None,
                                   enabled=True)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def ldap_users_table(self):
    try:
      ldap_users = self.user_controller.get_all_ldap_users()

      return self._render_template('/admin/users/ldapUserTable.html',
                                   ldap_users=ldap_users)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def resend_mail(self, user_id):
    try:
      user = self.user_controller.get_user_by_id(user_id)
      self.user_controller.resend_mail(user)
      self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def activate(self, user_id):
    try:
      user = self.user_controller.get_user_by_id(user_id)
      self.login_controller.activate_user(user.activation_str)
      self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['POST'])
  def modify_user(self, identifier=None, username=None, password=None,
                  priv=None, email=None, action='insert', disabled=None,
                  maingroup=None, ldap_users_table_length=None, apikey=None,
                  gpgkey=None, name=None, sirname=None):
    """
    modifies or inserts a user with the data of the post

    :param identifier: The identifier of the user,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param username: The username of the user
    :type username: String
    :param password: The password of the user
    :type password: String
    :param email: The email of the user
    :type email: String
    :param priv: Is the user privileged to access the administration section
    :type priv: Integer
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    try:

      if action == 'insertLDAP':
        user = self.user_controller.get_ldap_user(identifier)
        user, valid = self.user_controller.insert_ldap_user(user)
      else:
        self._check_if_valid_action(action)
        user = self.user_controller.populate_user(identifier, username, password,
                                                  priv, email, action, disabled, maingroup, apikey, gpgkey, name, sirname)
        if action == 'insert':
          user, valid = self.user_controller.insert_user(user)
        if action == 'update':
          user, valid = self.user_controller.update_user(user)
        if action == 'remove':
          user, valid = self.user_controller.remove_user(user)

      if valid:
        return self._return_ajax_ok()
      else:
        cb_values = self.user_controller.get_cb_group_values()
        return self._render_template('/admin/users/userModal.html',
                                     user=user,
                                     cb_values=cb_values,
                                     enabled=True)
    except ControllerException as error:
      return self._render_error_page(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  @cherrypy.tools.allow(methods=['GET'])
  def edit_user(self, userid):
    """
    renders the edit an user page

    :param userid: The user id of the desired displayed user
    :type userid: Integer

    :returns: generated HTML
    """
    try:
      user = self.user_controller.get_user_by_id(userid)
      cb_values = self.user_controller.get_cb_group_values()
      return self._render_template('/admin/users/userModal.html',
                                   user=user,
                                   cb_values=cb_values,
                                   enabled=True)
    except ControllerException as error:
      return self._render_error_page(error)
