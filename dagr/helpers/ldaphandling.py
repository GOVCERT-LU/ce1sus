# -*- coding: utf-8 -*-

"""
module containing interfaces classes related to LDAP

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.config import Configuration
from dagr.helpers.debug import Log
import ldap


# pylint:disable=R0903
class LDAPUser(object):
  """LDAP user container class"""
  def __init__(self):
    self.uid = None
    self.mail = None
    self.password = 'EXTERNALAUTH'
    self.displayName = None
    self.dn = None


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

  instance = None

  def __init__(self, configFile):
    self.__config = Configuration(configFile, 'LDAP')
    self.__users_dn = self.__config.get('users_dn')
    self.__tls = self.__config.get('usetls')
    LDAPHandler.instance = self

  def __getConnection(self):
    """
    Open the connection to the LDAP server
    """
    connection = None
    
    try:
      connection = ldap.initialize(self.__config.get('server'))
      if self.__tls:
        connection.start_tls_s()
    except ldap.LDAPError as e:
      Log.getLogger(self.__class__.__name__).fatal(e)
      raise ServerErrorException('LDAP error: ' + unicode(e))
    
    return connection


  def isUserValid(self, uid, password):
    """
    Checks if the user is valid

    :param uid:
    :type uid: String
    :param passowrd:
    :type password: String

    :returns: Boolean
    """
    try:
      self.__bindUser(uid, password)
    except LDAPException:
      return False
    
    return True

  def __bindUser(self, uid, password):
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
          connection = self.__getConnection()
          connection.simple_bind_s(self.__getUserDN(uid), password)
          self.__closeConnection(connection)
      except ldap.INVALID_CREDENTIALS:
        Log.getLogger(self.__class__.__name__
                        ).info(
                              'Username or password is invalid for {0}'.format(
                                                                          uid))
        raise InvalidCredentialsException('Username or password is invalid.')
    except ldap.LDAPError as e:
      Log.getLogger(self.__class__.__name__).fatal(e)
      raise ServerErrorException('LDAP error: {0}'.format(e))

  def __mapUser(self, ldapUser):
    """
    Maps the response from the LDAP server to userobject container

    :param user: list of attributes of the ldap user
    :type user: List

    :returns:
    """
    attributes = ldapUser[1]
    user = LDAPUser()
    user.dn = ldapUser[0]
    for key, value in attributes.iteritems():
      if hasattr(user, key):
      # Foo to prevent ascii errors as ldap module returns strings!
        try:
          setattr(user, key, unicode(value[0]))
        except UnicodeDecodeError:
          setattr(user, key, unicode(value[0], 'utf-8', errors='replace'))
    return user

  def getAllUsers(self):
    """
    Returns the attribute value

    :param uid:
    :type uid: String
    :param attributeName:
    :type attributeName: String

    :returns: String
    """
    filter_ = '(uid=*)'
    attributes = ["uid", "displayName", "mail"]
    try:
      connection = self.__getConnection()
      result = connection.search_s(self.__users_dn, ldap.SCOPE_SUBTREE,
                               filter_, attributes)
      self.__closeConnection(connection)
      userList = list()
      for user in result:
        user = self.__mapUser(user)
        userList.append(user)
      if len(userList) < 1:
        raise NothingFoundException('No  users were found')
    except ldap.LDAPError as e:
      Log.getLogger(self.__class__.__name__).fatal(e)
      raise ServerErrorException('LDAP error: {0}'.format(e))
    return userList

  def getUser(self, uid):
    """
    Returns the attribute value

    :param uid:
    :type uid: String
    :param attributeName:
    :type attributeName: String

    :returns: String
    """
    filter_ = '(uid={0})'.format(uid)
    attributes = ["uid", "displayName", "mail", "dc"]

    try:
      connection = self.__getConnection()
      result = connection.search_s(self.__users_dn,
                                          ldap.SCOPE_SUBTREE,
                                          filter_,
                                          attributes)
      self.__closeConnection(connection)
      # forcibly take only first user
      user = self.__mapUser(result[0])
      return user
    except ldap.LDAPError as e:
      Log.getLogger(self.__class__.__name__).fatal(e)
      raise ServerErrorException('LDAP error: {0}'.format(e))

  def __getUserDN(self, uid):
    """
    Returns the User domain name string

    :param uid:
    :type uid: String

    :returns: String
    """
    user = self.getUser(uid)
    return user.dn

  def __closeConnection(self, connection):
    """
    close the connection
    """
    try:
      connection.unbind_s()
    except ldap.LDAPError as e:
      Log.getLogger(self.__class__.__name__).fatal(e)

  @classmethod
  def getInstance(cls):
    """
      Returns an instance

      :returns: LDAPHandler
    """
    if LDAPHandler.instance is None:
      raise NotInitializedException('LDAPHandler has not been initialized')
    else:
      return LDAPHandler.instance
