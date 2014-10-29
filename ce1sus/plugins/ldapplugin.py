# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 28, 2014
"""
from ce1sus.controllers.admin.user import UserController
from ce1sus.helpers.common.ldaphandling import LDAPHandler, LDAPException, NothingFoundException
from ce1sus.plugins.base import plugin_web_method, BasePlugin, PluginException
from ce1sus.controllers.base import ControllerException

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class LdapPlugin(BasePlugin):

  def __init__(self, config):
    BasePlugin.__init__(self, config)
    self.ldap_handler = LDAPHandler(config)
    # TODO: find a way to use the rest api instead of using the controller
    self.user_controller = UserController(config)

  def __convert_ldap_user(self, ldap_user):
    user = self.user_controller.populate_user(None,
                                              ldap_user.uid,
                                              'EXTERNALAUTH',
                                              0,
                                              ldap_user.mail,
                                              'insert',
                                              0,
                                              None,
                                              None,
                                              None,
                                              ldap_user.name,
                                              ldap_user.sir_name)
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
