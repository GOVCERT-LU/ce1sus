# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug 26, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, privileged, require_referer
from dagr.web.helpers.pagination import Paginator
from dagr.helpers.ldaphandling import LDAPHandler, LDAPException
from dagr.db.broker import IntegrityException, BrokerException, \
  ValidationException, DeletionException
import types as types
from ce1sus.brokers.permission.userbroker import UserBroker
from ce1sus.brokers.permission.groupbroker import GroupBroker


class UserController(Ce1susBaseController):
  """Controller handling all the requests for users"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.user_broker = self.broker_factory(UserBroker)
    self.group_broker = self.broker_factory(GroupBroker)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the user page

    :returns: generated HTML
    """
    template = self._get_template('/admin/users/userBase.html')
    return self.clean_html_code(template.render())

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def left_content(self):
    """
    renders the left content of the user index page

    :returns: generated HTML
    """
    template = self._get_template('/admin/users/userLeft.html')
    users = self.user_broker.get_all()
    return self.clean_html_code(template.render(users=users,
                           useLDAP=self._get_config_variable('useldap')))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def right_content(self, userid=0, user=None):
    """
    renders the right content of the user index page

    :param userid: The user id of the desired displayed user
    :type userid: Integer
    :param user: Similar to the previous attribute but prevents
                      additional loadings
    :type user: User

    :returns: generated HTML
    """
    template = self._get_template('/admin/users/userRight.html')
    if user is None:
      if userid is None or userid == 0:
        user = None
      else:
        user = self.user_broker.get_by_id(userid)
    else:
      user = user
    # populate the CB
    groups = self.group_broker.get_all()
    cb_values = dict()
    for group in groups:
      cb_values[group.name] = group.identifier
    return self.clean_html_code(template.render(userDetails=user,
                           cb_values=cb_values))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def add_user(self):
    """
    renders the add a user page

    :returns: generated HTML
    """
    template = self._get_template('/admin/users/userModal.html')
    groups = self.group_broker.get_all()
    cb_values = dict()
    for group in groups:
      cb_values[group.name] = group.identifier
    return self.clean_html_code(template.render(user=None,
                                              cb_values=cb_values))

  @require(privileged())
  @cherrypy.expose
  def ldap_users_table(self):
    """
    renders the table with the ldap users

    :returns: generated HTML
    """
    template = self._get_template('/admin/users/ldapUserTable.html')
    labels = [{'radio':'#'},
              {'uid':'username'},
              {'mail':'Email'},
              {'displayName':'Name'}
              ]

    ldap_handler = LDAPHandler.get_instance()
    ldap_paginator = Paginator(items=ldap_handler.get_all_users(),
                          labelsAndProperty=labels)
    return self.clean_html_code(template.render(ldap_paginator=ldap_paginator))

  # pylint: disable=R0913
  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def modify_user(self, identifier=None, username=None, password=None,
                 priv=None, email=None, action='insert', disabled=None,
                 maingroup=None, ldap_users_table_length=None, apikey=None):
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
    template = self._get_template('/admin/users/userModal.html')
    del ldap_users_table_length
    user = self.user_broker.buildUser(identifier, username, password,
                 priv, email, action, disabled, maingroup, apikey)
    try:
      if action == 'insert':
        self.user_broker.insert(user, validate=True)
      if action == 'insertLDAP':
        # check if a user with the users username does not already exists
        existing_user = None
        try:
          existing_user = self.user_broker.getUserByUserName(user.username)
        except BrokerException:
          pass
        if existing_user is None:
          self.user_broker.insert(user, validate=False)
        else:
          return 'User with the username ' + user.username + 'already exits'
      if action == 'update':
        self.user_broker.update(user, validate=False)
      if action == 'remove':
        if (user.identifier == '1'):
          raise DeletionException('First user cannot be removed.')
        self.user_broker.remove_by_id(user.identifier)
      return self._return_ajax_ok()
    except IntegrityException as error:
      self._get_logger().info('User tried to delete referenced user.')
      return ('Cannot delete user. The user is referenced by elements.'
                    + ' Disable this user instead.')
    except LDAPException as error:
      self._get_logger().error('An unexpected LDAPException occurred: {0}'
                             .format(error))
      return "Error {0}".format(error)
    except ValidationException:
      self._get_logger().debug('User is invalid')
      groups = self.group_broker.get_all()
      cb_values = dict()
      for group in groups:
        cb_values[group.name] = group.identifier
      return self._return_ajax_post_error() + self.clean_html_code(
                                                          template.render(
                                                          user=user,
                                                          cb_values=cb_values))
    except DeletionException as error:
      self._get_logger().info('User tried to delete undeletable user.')
      return "Error {0}".format(error)
    except BrokerException as error:
      self._get_logger().error('An unexpected BrokerException occurred: {0}'
                             .format(error))
      return "Error {0}".format(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_user(self, userid):
    """
    renders the edit a user page

    :param userid: The user id of the desired displayed user
    :type userid: Integer

    :returns: generated HTML
    """
    template = self._get_template('/admin/users/userModal.html')
    error_msg = None
    try:
      user = self.user_broker.get_by_id(userid)
      groups = self.group_broker.get_all()
      cb_values = dict()
      for group in groups:
        cb_values[group.name] = group.identifier
    except BrokerException as error:
      self._get_logger().error('An unexpected error occurred: {0}'.format(error))
      error_msg = 'An unexpected error occurred: {0}'.format(error)
    return self.clean_html_code(template.render(user=user,
                                              error_msg=error_msg,
                                              cb_values=cb_values))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_user_groups(self, user_id, operation, remaining_groups=None,
                     user_groups=None):
    """
    modifies the relation between a user and his groups

    :param user_id: The user_id of the user
    :type user_id: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remaining_groups: The identifiers of the groups which the user is not
                            attributed to
    :type remaining_groups: Integer array
    :param user_groups: The identifiers of the groups which the user is
                       attributed to
    :type user_groups: Integer array

    :returns: generated HTML
    """
    try:
      if operation == 'add':
        if not (remaining_groups is None):
          if isinstance(remaining_groups, types.StringTypes):
            self.group_broker.addGroupToUser(user_id, remaining_groups)
          else:
            for group_id in remaining_groups:
              self.group_broker.addGroupToUser(user_id, group_id, False)
            self.group_broker.session.commit()
      else:
        if not (user_groups is None):
          if isinstance(user_groups, types.StringTypes):
            self.group_broker.removeGroupFromUser(user_id, user_groups)
          else:
            for group_id in user_groups:
              self.group_broker.removeGroupFromUser(user_id, group_id, False)
            self.group_broker.session.commit()
      return self._return_ajax_ok()
    except BrokerException as error:
      return "Error {0}".format(error)
