# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 26, 2014
"""
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.common.broker import NothingFoundException, BrokerException
from ce1sus.helpers.pluginfunctions import is_plugin_available, get_plugin_function
from ce1sus.plugins.base import PluginException
from datetime import datetime


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ActivationTimedOut(Exception):
  pass


class LoginController(BaseController):

  def __init__(self, config, session=None):
    super(BaseController, self).__init__(config, session)
    salt = self.config.get('ce1sus', 'salt', None)
    if salt:
      self.salt = salt
    else:
      raise ControllerException('Salt was not defined in ce1sus.conf')

  def get_user_by_usr_pwd(self, username, password):
    """
    Checks if the credentials are valid

    :param username: The username
    :type username: String
    :param password: The password of the user in plain text?
    :typee password: String

    :returns: Boolean
    """
    try:
      user = None
      try:
                # check if ldap plugin is available
        if is_plugin_available('ldap', self.config):
          ldap_password_identifier = get_plugin_function('ldap', 'get_ldap_pwd_identifier', self.config, 'internal_plugin')()
          try:
            user = self.user_broker.getUserByUsernameAndPassword(username, ldap_password_identifier, None)
            # user is present in DB, check if usr and pwd matching
            method = get_plugin_function('ldap', 'is_user_valid', self.config, 'internal_plugin')
            valid = method(username, password)
            if not valid:
              user = None
          except (NothingFoundException, PluginException) as error:
            user = None

        # check if user is a pure DBUser
        if user is None:
          # the user was not specified as ldap user use traditional login
          user = self.user_broker.getUserByUsernameAndPassword(username, password, self.salt)

      except NothingFoundException as error:
        self.logger.info(('A login attempt was made with username "{0}" '
                          + 'but the user was not defined.').format(username))
      except BrokerException as error:
        self.logger.critical(error)

      if user:
        # check if a user was found and if it was not disabled
        self.logger.debug('Checking if user {0} is allowed'.format(user.username))
        if user.can_access:
          return user
      else:
        raise ControllerException('No user was found matching the given username and password')
    except BrokerException as error:
      raise ControllerException(error)

  def update_last_login(self, user):
    """
    Updates the last login time for the user by the username and returns the user

    :param username: the username
    :type username: String

    :returns: User
    """
    try:
      user.last_login = datetime.utcnow()
      self.user_broker.update(user)
    except BrokerException as error:
      raise ControllerException(error)

  def get_user_by_username(self, username):
    try:
      return self.user_broker.getUserByUserName(username)
    except BrokerException as error:
      raise ControllerException(error)

  def get_user_by_apikey(self, apikey):
    try:
      return self.user_broker.get_user_by_api_key(apikey)
    except BrokerException as error:
      raise ControllerException(error)
