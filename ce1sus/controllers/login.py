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


class LoginController(Ce1susBaseController):
  """
  Controls all login related actions
  """

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.user_broker = self.broker_factory(UserBroker)
    self.ldap_handler = LDAPHandler(config)

  def get_user_y_usr_pwd(self, username, password):
    """
    Checks if the credentials are valid

    :param username: The username
    :type username: String
    :param password: The password of the user in plain text?
    :typee password: String

    :returns: Boolean
    """

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

    # check if a user was found and if it was not disabled
    if user:
      if user.disabled == 1:
        return None
      else:
        return user
    else:
      return None

    return user

  def get_user_by_apiKey(self, api_key):
    """returns the user by api key"""
    try:
      return self.user_broker.get_user_by_api_key(api_key)
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
