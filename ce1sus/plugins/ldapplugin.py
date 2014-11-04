# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 28, 2014
"""
from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import ControllerException
from ce1sus.db.classes.user import User
from ce1sus.helpers.common.ldaphandling import LDAPHandler, LDAPException, NothingFoundException
from ce1sus.plugins.base import plugin_web_method, BasePlugin, PluginException, plugin_internal_method


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class LdapPlugin(BasePlugin):

  def __init__(self, config):
    BasePlugin.__init__(self, config)
    self.ldap_handler = LDAPHandler(config)
    self.user_controller = UserController(config)

  def __convert_ldap_user(self, ldap_user):
    user = User()
    user.username = ldap_user.uid
    user.password = self.get_ldap_pwd_identifier()
    user.email = ldap_user.mail
    if not user.email:
      ldap_user = self.ldap_handler.get_user(user.username)
    user.name = ldap_user.name
    user.sirname = ldap_user.sir_name
    return user

  def __get_all(self):
    try:
      ldap_users = self.ldap_handler.get_all_users()
      result = list()
      for user in ldap_users:
        result.append(user.to_dict())
      return result
    except NothingFoundException:
      return []
    except LDAPException as error:
      raise PluginException(error)

  def __insert_user(self, uid):
    try:
      if uid:
        ldap_user = self.ldap_handler.get_user(uid)
        db_user = self.__convert_ldap_user(ldap_user)

        self.user_controller.insert_user(db_user)

        # return dict of user
        return db_user.to_dict()
      else:
        raise PluginException('No uid was specified to be inserted')

    except (LDAPException, ControllerException) as error:
      raise PluginException(error)

  @plugin_web_method
  def user(self, http_method, params):
    if http_method == 'GET':
      if params:
        pass
      else:
        return self.__get_all()
    elif http_method == 'POST':
      return self.__insert_user(params.get('uid', None))
    elif http_method == 'PUT':
      pass
    elif http_method == 'DELETE':
      pass
    else:
      raise PluginException('Method {0} is not defined'.format(http_method))

  @plugin_internal_method
  def get_ldap_pwd_identifier(self):
    return 'EXTERNALAUTH'

  @plugin_internal_method
  def is_user_valid(self, username, password):
    try:
      return self.ldap_handler.is_valid_user(username, password)
    except LDAPException as error:
      raise PluginException(error)
