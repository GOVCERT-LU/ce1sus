# -*- coding: utf-8 -*-

"""
module containing interfaces classes related to LDAP

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.debug import Log
import ldap


# pylint:disable=R0903
class LDAPUser(object):
  """LDAP user container class"""
  def __init__(self):
    self.uid = None
    self.mail = None
    self.password = 'EXTERNALAUTH'
    self.sir_name = None
    self.name = None
    self.dn_string = None

  def __clean_value(self, value):
    if value:
      return unicode(value, errors='replace')
    return value

  @property
  def display_name(self):
    return '{0} {1}'.format(self.__clean_value(self.sir_name), self.__clean_value(self.name))


class LDAPException(Exception):
  """LDAP Error"""
  pass


class NothingFoundException(LDAPException):
  """Invalid Error"""
  pass


class InvalidCredentialsException(LDAPException):
  """Invalid Error"""
  pass


class ServerErrorException(LDAPException):
  """Server Error"""
  pass


class NotInitializedException(LDAPException):
  """Server Error"""
  pass


class LDAPHandler(object):
  "LDAP Handler"

  def __init__(self, config):

    self.__config_section = config.get_section('LDAP')
    self.__users_dn = self.__config_section.get('users_dn')
    self.__tls = self.__config_section.get('usetls')
    self.logger = Log(config)

  def _get_logger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return self.logger.get_logger(self.__class__.__name__)

  def __get_connection(self):
    """
    Open the connection to the LDAP server
    """
    try:
      connection = ldap.initialize(self.__config_section.get('server'))
      if self.__tls:
        connection.start_tls_s()
        return connection
    except ldap.LDAPError as error:
      self._get_logger().fatal(error)
      raise ServerErrorException('LDAP error: {0}'.format(error))

  def is_valid_user(self, uid, password):
    """
    Checks if the user is valid

    :param uid:
    :type uid: String
    :param passowrd:
    :type password: String

    :returns: Boolean
    """
    try:
      self.__bind_user(uid, password)
    except LDAPException:
      return False

    return True

  def __bind_user(self, uid, password):
    """
    Bind/authenticate with a user with appropriate rights to add objects

    :param uid:
    :type uid: String
    :param passowrd:
    :type password: String
    """
    try:
      try:
        if not (uid is None or password is None):
          connection = self.__get_connection()
          user_dn = self.__get_user_dn(uid)
          connection.simple_bind_s(user_dn, password)
          self.__close_connection(connection)
      except ldap.INVALID_CREDENTIALS:
        self._get_logger().info('Username or password is invalid for {0}'.format(
                                                                          uid))
        raise InvalidCredentialsException('Username or password is invalid.')
    except ldap.LDAPError as error:
      self._get_logger().fatal(error)
      raise ServerErrorException('LDAP error: {0}'.format(error))

  @staticmethod
  def __get_clean_value(dictionary, identifier):
    value = dictionary.get(identifier, None)
    if value:
      value = value[0]
      # Foo to prevent ascii errors as ldap module returns strings!
      try:
        return value
      except UnicodeDecodeError:
        return unicode(value, 'utf-8', errors='replace')
    else:
      return None

  @staticmethod
  def __map_user(ldap_user):
    """
    Maps the response from the LDAP server to userobject container

    :param ldap_user: list of attributes of the ldap user
    :type ldap_user: List

    :returns: LDAPUser
    """
    attributes = ldap_user[1]
    user = LDAPUser()
    user.dn_string = ldap_user[0]
    user.uid = LDAPHandler.__get_clean_value(attributes, 'uid')
    user.mail = LDAPHandler.__get_clean_value(attributes, 'mail')
    user.password = 'EXTERNALAUTH'
    user.sir_name = LDAPHandler.__get_clean_value(attributes, 'sn')
    user.name = LDAPHandler.__get_clean_value(attributes, 'givenName')
    return user

  def __get_all_users(self):
    """
    Returns the attribute value

    :param uid:
    :type uid: String
    :param attributeName:
    :type attributeName: String

    :returns: String
    """
    filter_ = '(uid=*)'
    attributes = None
    user_list = None
    try:
      connection = self.__get_connection()
      result = connection.search_s(self.__users_dn, ldap.SCOPE_SUBTREE,
                               filter_, attributes)

      user_list = list()
      for user in result:
        user = LDAPHandler.__map_user(user)
        user_list.append(user)
      if len(user_list) < 1:
        raise NothingFoundException('No  users were found')
    except ldap.LDAPError as error:
      self._get_logger().fatal(error)
      raise ServerErrorException('LDAP error: {0}'.format(error))
    self.__close_connection(connection)
    return user_list

  def get_all_users(self):
    users = self.__get_all_users()
    if users:
      if users[0].mail:
        return users
      else:
        return self.__get_all_users()

  def get_user(self, uid):
    """
    Returns the attribute value

    :param uid:
    :type uid: String
    :param attributeName:
    :type attributeName: String

    :returns: String
    """
    filter_ = '(uid={0})'.format(uid)
    attributes = None

    try:
      connection = self.__get_connection()
      result = connection.search_s(self.__users_dn,
                                          ldap.SCOPE_SUBTREE,
                                          filter_,
                                          attributes)
      self.__close_connection(connection)
      # forcibly take only first user
      user = LDAPHandler.__map_user(result[0])
      return user
    except ldap.LDAPError as error:
      self._get_logger().fatal(error)
      raise ServerErrorException('LDAP error: {0}'.format(error))

  def __get_user_dn(self, uid):
    """
    Returns the User domain name string

    :param uid:
    :type uid: String

    :returns: String
    """
    user = self.get_user(uid)
    return user.dn_string

  def __close_connection(self, connection):
    """
    close the connection
    """
    try:
      connection.unbind_s()
    except ldap.LDAPError as error:
      self._get_logger().fatal(error)
