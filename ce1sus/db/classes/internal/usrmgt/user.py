# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 28, 2014
"""
from ce1sus.helpers.bitdecoder import BitBase
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator
import re
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import DateTime, Integer, Boolean

from ce1sus.common import merge_dictionaries
from ce1sus.db.classes.internal.core import BaseObject, BigIntegerType, UnicodeType, UnicodeTextType
from ce1sus.db.classes.internal.usrmgt.group import Group
from ce1sus.db.common.session import Base


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class UserRights(BitBase):

  """
  The __bit_value is defined as follows:
  [0] : User is privileged
  [1] : User can validate
  [2] : User can manage it's own group
  """

  ACTIVATED = 0
  PRIVILEGED = 1
  VALIDATE = 2
  MANAGE_GROUP = 3

  @property
  def access_admin_area(self):
    return (not self.disabled) or self.privileged or self.validate

  @property
  def privileged(self):
    return self._get_value(UserRights.PRIVILEGED)

  @privileged.setter
  def privileged(self, value):
    self._set_value(UserRights.PRIVILEGED, value)

  @property
  def disabled(self):
    return not self._get_value(UserRights.ACTIVATED)

  @disabled.setter
  def disabled(self, value):
    self._set_value(UserRights.ACTIVATED, not value)

  @property
  def validate(self):
    return self._get_value(UserRights.VALIDATE)

  @validate.setter
  def validate(self, value):
    self._set_value(UserRights.VALIDATE, value)

  @property
  def manage_group(self):
    return self._get_value(UserRights.MANAGE_GROUP)

  @manage_group.setter
  def manage_group(self, value):
    self._set_value(UserRights.MANAGE_GROUP, value)

  @staticmethod
  def append_to_string(text, string):
    result = text
    if len(result) > 1:
      result = u'{0},{1}'.format(result, string)
    else:
      result = u'{0}{1}'.format(result, string)
    return result

  def to_dict(self, complete=True, inflated=False, event_permissions=None, user=None):
    return {'disabled': self.disabled,
            'priviledged': self.privileged,
            'manage_group': self.manage_group,
            'validate': self.validate}


class User(BaseObject, Base):
  name = Column('name', UnicodeType(255), nullable=False)
  sirname = Column('sirname', UnicodeType(255), nullable=False)
  username = Column('username', UnicodeType(255), nullable=False, unique=True)
  password = Column('password', UnicodeType(255), nullable=False, unique=True)
  last_login = Column('last_login', DateTime)
  email = Column('email', UnicodeType(255), unique=True)
  api_key = Column('apikey', UnicodeType(255), index=True, unique=True)
  gpg_key = Column('gpg_key', UnicodeTextType())
  activated = Column('activated', DateTime)
  activation_sent = Column('activation_sent', DateTime)
  activation_str = Column('activation_str', UnicodeType(255))
  dbcode = Column('code', Integer, default=0, nullable=False)
  __bit_code = None

  group_id = Column('group_id', BigIntegerType, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), index=True)
  group = relationship(Group, lazy='joined')
  plain_password = None
  notifications = Column('notifications', Boolean, default=True, nullable=False)

  @property
  def can_access(self):
    return (not self.permissions.disabled) and self.is_activated

  @property
  def is_activated(self):
    return self.activated

  @property
  def permissions(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = UserRights('0', self)
      else:
        self.__bit_code = UserRights(self.dbcode, self)
    return self.__bit_code

  @property
  def display_name(self):
    return '{0} {1}'.format(self.sirname, self.name)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO: Edit cannot change username!
    # TODO: Verify validation of User Object
    if not (self.password or self.username):
      return False
    ObjectValidator.validateAlNum(self,
                                  'username',
                                  minLength=3,
                                  maxLength=254)
    # Don't update if the password is already a hash
    if self.password:
      if not (self.password == 'EXTERNALAUTH') and re.match('^[0-9a-f]{40}$', self.password) is None:
        ObjectValidator.validateRegex(self,
                                      'password',
                                      r'(?=^.{8,}$)(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[\W_])(?=^.*[^\s].*$).*$',
                                      'Password has to be set and contain Upper and Lower cases, symbols and numbers and have at least a length of 8'
                                      )

    ObjectValidator.validateEmailAddress(self, 'email')
    ObjectValidator.validateAlNum(self, 'name', minLength=3, withSymbols=True)
    ObjectValidator.validateAlNum(self, 'sirname', minLength=3, withSymbols=True)

    # if self.gpg_key:
    #  ObjectValidator.validateRegex(self,
    #                                'gpg_key',
    #                                '-----BEGIN PGP PUBLIC KEY BLOCK-----(.*?)-----END PGP PUBLIC KEY BLOCK-----',
    #                                'GPG Key not under the right format')
    if self.last_login is not None:
      ObjectValidator.validateDateTime(self, 'last_login')
    return ObjectValidator.isObjectValid(self)

  def to_dict(self, cache_object):
    if self.group:
      group_id = self.group.uuid
    else:
      group_id = None
    if cache_object.complete:
      result = {
              'name': self.convert_value(self.name),
              'activated': self.convert_value(self.activated),
              'activation_send': self.convert_value(self.activation_sent),
              'activation_str': self.convert_value(self.activation_str),
              'api_key': self.convert_value(self.api_key),
              'dbcode': self.convert_value(self.dbcode),
              'email': self.convert_value(self.email),
              'gpg_key': self.convert_value(self.gpg_key),
              'group_id': self.convert_value(group_id),
              'permissions': self.attribute_to_dict(self.permissions, cache_object),
              'group': self.attribute_to_dict(self.group, cache_object),
              'last_login': self.convert_value(self.last_login),
              'password': self.convert_value(self.password),
              'sirname': self.convert_value(self.sirname),
              'username': self.convert_value(self.username),
              'notifications': self.convert_value(self.notifications)
              }
    else:
      result = {
              'username': self.username
              }

    parent_dict = BaseObject.to_dict(self, cache_object)
    return merge_dictionaries(result, parent_dict)
