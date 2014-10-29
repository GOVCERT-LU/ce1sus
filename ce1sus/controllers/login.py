# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 26, 2014
"""
from ce1sus.controllers.base import BaseController
from ce1sus.db.common.broker import NothingFoundException, BrokerException
from ce1sus.helpers.common.datumzait import DatumZait
from ce1sus.helpers.common.ldaphandling import LDAPHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ActivationTimedOut(Exception):
  pass


class LoginController(BaseController):

  def __init__(self, config):
    BaseController.__init__(self, config)
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
        if self.config.get('ce1sus', 'useldap', False):
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
        self.logger.info(('A login attempt was made with username "{0}" '
                          + 'but the user was not defined.').format(username))
      except BrokerException as error:
        self.logger.critical(error)
      if user:
        # check if a user was found and if it was not disabled
        self.__check_user(user)
      else:
        self.raise_exception('User was none, leads to a compromized db')
      return user
    except BrokerException as error:
      self.raise_exception(error)

  def __check_user(self, user):
    """Checks if the user is allowed to login"""
    self.logger.debug('Checking if user {0} is allowed'.format(user.username))
    if user:
      if user.can_access:
        return user
      else:
        raise BrokerException('User {0} is not allowed'.format(user.username))
    else:
      raise BrokerException('User {0} is not allowed'.format(user.username))

  def update_last_login(self, user):
    """
    Updates the last login time for the user by the username and returns the user

    :param username: the username
    :type username: String

    :returns: User
    """
    try:
      # TODO: set correct time
      # user.last_login = DatumZait.utcnow()
      self.user_broker.update(user)
    except BrokerException as error:
      self.raise_exception(error)
