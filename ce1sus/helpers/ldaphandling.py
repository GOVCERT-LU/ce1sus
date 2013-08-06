"""module containing interfaces classes related to LDAP"""

from ce1sus.helpers.config import Configuration
from ce1sus.helpers.debug import Logger
import ldap
import types

class LDAPUser(object):
  def __init__(self):
    self.uid = None
    self.mail = None
    self.password = 'EXTERNALAUTH'
    self.displayName = None

class LDAPException(Exception):
  """LDAP Error"""
  def __init__(self, message):
    Exception.__init__(self, message)

class NothingFoundException(LDAPException):
  """Invalid Error"""
  def __init__(self, message):
    LDAPException.__init__(self, message)

class InvalidCredentialsException(LDAPException):
  """Invalid Error"""
  def __init__(self, message):
    LDAPException.__init__(self, message)

class ServerErrorException(LDAPException):
  """Server Error"""
  def __init__(self, message):
    LDAPException.__init__(self, message)

class NotInitializedException(LDAPException):
  """Server Error"""
  def __init__(self, message):
    LDAPException.__init__(self, message)

class LDAPHandler(object):
  "LDAP Handler"


  def __init__(self, configFile):
    self.__config = Configuration(configFile, 'LDAP')

    self.__connection = None

    self.__users_dn = self.__config.get('users_dn')

    self.__tls = self.__config.get('usetls')



    LDAPHandler.instance = self

  def open(self):
    self.__connection = ldap.initialize(self.__config.get('server'))
    try:
      if self.__tls:
        self.__connection.start_tls_s()
    except ldap.LDAPError as e:
      Logger.getLogger(self.__class__.__name__).fatal(e)
      raise ServerErrorException('LDAP error: ' + str(e))


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
      return True
    except LDAPException:
      return False

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
          self.__connection.simple_bind_s(self.__getUserDN(uid), password)
      except ldap.INVALID_CREDENTIALS:
        Logger.getLogger(self.__class__.__name__
                        ).info('Username or password is invalid for {0}'.format(
                                                                          uid))
        raise InvalidCredentialsException('Username or password is invalid.')
    except ldap.LDAPError as e:
      Logger.getLogger(self.__class__.__name__).fatal(e)
      raise ServerErrorException('LDAP error: {0}'.format(e))


  def __mapUser(self, user):
    for attributes in user:
      if isinstance(attributes, types.DictType):
        user = LDAPUser()
        for key, value in attributes.iteritems():
          if hasattr(user, key):
            setattr(user, key, value[0])

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
      result = self.__connection.search_s(self.__users_dn, ldap.SCOPE_SUBTREE,
                               filter_, attributes)
      # dierft nemmen 1 sinn
      userList = list()
      for user in result:
        user = self.__mapUser(user)
        userList.append(user)
      if len(userList) < 1:
        raise NothingFoundException('No  users were found')
    except ldap.LDAPError as e:
      Logger.getLogger(self.__class__.__name__).fatal(e)
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
    filter_ = '(uid=*)'

    attributes = ["uid", "displayName", "mail"]

    try:
      result = self.__connection.search_s(self.__getUserDN(uid), ldap.SCOPE_SUBTREE,
                               filter_, attributes)
      # dierft nemmen 1 sinn
      for user in result:
        user = self.__mapUser(user)

    except ldap.LDAPError as e:
      Logger.getLogger(self.__class__.__name__).fatal(e)
      raise ServerErrorException('LDAP error: {0}'.format(e))
    return user



  def getUserAttribute(self, uid, attributeName):
    """
    Returns the attribute value

    :param uid:
    :type uid: String
    :param attributeName:
    :type attributeName: String

    :returns: String
    """
    filter_ = '(uid=' + uid + ')'
    userdn = self.__getUserDN(uid)
    try:
      result = self.__connection.search_s(userdn, ldap.SCOPE_SUBTREE,
                               filter_, [attributeName])
    except ldap.LDAPError as e:
      Logger.getLogger(self.__class__.__name__).fatal(e)
      raise ServerErrorException('LDAP error: {0}'.format(e))
    attribute = None
    # dierft nemmen 1 sinn
    for tuple in result:
      for item in tuple:
        if isinstance(item, types.DictType):
          attribute = item[attributeName][0]
    return attribute

  def __getUserDN(self, uid):
    """
    Returns the User domain name string

    :param uid:
    :type uid: String

    :returns: String
    """
    return 'uid=' + uid + ',' + self.__users_dn

  def close(self):
    """
    close the connection
    """
    try:
      self.__connection.unbind_s()
    except ldap.LDAPError as e:
      Logger.getLogger(self.__class__.__name__).fatal(e)

  @staticmethod
  def getInstance():
    """
      Returns an instance

      :returns: LDAPHandler
    """
    if hasattr(LDAPHandler, 'instance'):
      return LDAPHandler.instance
    else:
      raise NotInitializedException('LDAPHandler has not been initialized')
