# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
import re

from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.user import User
from ce1sus.helpers.common.hash import hashSHA1
from ce1sus.helpers.pluginfunctions import is_plugin_available, get_plugin_function
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminUserHandler(RestBaseHandler):

  PASSWORD_MASK = '*******************'

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.user_controller = UserController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'POST', 'PUT', 'DELETE'])
  @require(privileged())
  def user(self, **args):
    try:
      method = args.get('method')
      path = args.get('path')
      details = self.get_detail_value(args)
      json = args.get('json')
      if method == 'GET':

        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          # TODO: add inflate
          user = self.user_controller.get_user_by_id(uuid)
          if details:
            password = '*******************'
            if is_plugin_available('ldap', self.config):
              ldap_password_identifier = get_plugin_function('ldap', 'get_ldap_pwd_identifier', self.config, 'internal_plugin')()

              if user.password == ldap_password_identifier:
                password = ldap_password_identifier

            user.password = password

            return user.to_dict()
          else:
            return user.to_dict(complete=False)
        else:
          # else return all
          users = self.user_controller.get_all_users()
          result = list()
          for user in users:
            if details:
              password = AdminUserHandler.PASSWORD_MASK
              if is_plugin_available('ldap', self.config):
                ldap_password_identifier = get_plugin_function('ldap', 'get_ldap_pwd_identifier', self.config, 'internal_plugin')()
                password = ldap_password_identifier
              user.password = password
              result.append(user.to_dict())
            else:
              result.append(user.to_dict(complete=False))
          return result
      elif method == 'POST':
        # Add new user
        user = User()
        user.populate(json)
        user.password = hashSHA1(user.plain_password, user.username)
        self.user_controller.insert_user(user)
        return user.to_dict()
      elif method == 'PUT':
        # update user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          user = self.user_controller.get_user_by_id(uuid)
          user.populate(json)
          # Do not update the password if it matches the masking
          if not re.match(r'^\*{8,}$', user.plain_password):
            user.password = hashSHA1(user.plain_password, user.username)
          self.user_controller.update_user(user)
          return user.to_dict()
        else:
          raise RestHandlerException(u'Cannot update user as no identifier was given')

      elif method == 'DELETE':
        # Remove user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          self.user_controller.remove_user_by_id(uuid)
          return 'Deleted user'
        else:
          raise RestHandlerException(u'Cannot delete user as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
