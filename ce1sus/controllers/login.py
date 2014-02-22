# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from ce1sus.brokers.permission.userbroker import UserBroker
from dagr.helpers.datumzait import DatumZait
from dagr.db.broker import BrokerException, NothingFoundException
from dagr.helpers.ldaphandling import LDAPHandler
import math


class ActivationTimedOut(Exception):
  pass


class LoginController(Ce1susBaseController):
  """
  Controls all login related actions
  """

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.user_broker = self.broker_factory(UserBroker)
    self.ldap_handler = LDAPHandler(config)

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
        if self._get_config_variable('useldap'):
          try:
            user = self.user_broker.getUserByUsernameAndPassword(username,
                                                               'EXTERNALAUTH')
          except NothingFoundException as error:
            user = None

        if user is None:
          # the user was not specified as ldap user use traditional login
          user = self.user_broker.getUserByUsernameAndPassword(username, password)
        else:
          # the user was specified as ldap user
          valid = self.ldap_handler.is_valid_user(username, password)
          if not valid:
            user = None
      except NothingFoundException as error:
        self._get_logger().info(('A login attempt was made with username "{0}" '
                                 + 'but the user was not defined.').format(username))
      except BrokerException as error:
        self._get_logger().critical(error)
      if user:
        # check if a user was found and if it was not disabled
        self.__check_user(user)
      else:
        self._raise_exception('User was none, leads to a compromized db')
      return user
    except BrokerException as error:
      self._raise_exception(error)

  def __check_user(self, user):
    """Checks if the user is allowed to login"""
    self._get_logger().debug('Checking if user {0} is allowed'.format(user.username))
    if user:
      if user.allowed:
        return user
      else:
        raise BrokerException('User {0} is not allowed'.format(user.username))
    else:
      raise BrokerException('User {0} is not allowed'.format(user.username))

  def get_user_by_apikey(self, api_key):
    """returns the user by api key"""
    try:
      user = self.user_broker.get_user_by_api_key(api_key)
      # check if a user was found and if it was not disabled
      self.__check_user(user)
      return user

    except BrokerException as error:
      self._raise_exception(error)

  def update_last_login(self, user):
    """
    Updates the last login time for the user by the username and returns the user

    :param username: the username
    :type username: String

    :returns: User
    """
    try:
      user.last_login = DatumZait.utcnow()
      self.user_broker.update(user)
    except BrokerException as error:
      self._raise_exception(error)

  def activate_user(self, activation_str):
    try:
      now = DatumZait.utcnow()
      user = self.user_broker.get_user_by_act_str(activation_str)
      time_diff = now - user.activation_sent
      if math.floor((time_diff.seconds) / 3600) >= 24:
        raise ActivationTimedOut('ActivationLink expired.')
      if user.disabled == 1:
        raise BrokerException('User is disabled')
      user.activated = now
      user.activation_str = None
      self.user_broker.update(user)
    except BrokerException as error:
      self._raise_exception(error)
