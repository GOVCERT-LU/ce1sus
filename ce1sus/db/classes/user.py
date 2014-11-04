# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 28, 2014
"""
from _mysql import result
import re
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, DateTime, Text, Integer, BIGINT

from ce1sus.db.classes.basedbobject import SimpleLogingInformations
from ce1sus.db.classes.group import Group
from ce1sus.db.common.session import Base
from ce1sus.helpers.bitdecoder import BitBase
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class UserRights(BitBase):

  """
  The __bit_value is defined as follows:
  [0] : User is privileged
  [1] : User can validate
  [2] : User can set group via rest inserts
  """

  ACTIVATED = 0
  PRIVILEGED = 1
  VALIDATE = 2
  SET_GROUP = 3

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
  def set_group(self):
    return self._get_value(UserRights.SET_GROUP)

  @set_group.setter
  def set_group(self, value):
    self._set_value(UserRights.SET_GROUP, value)

  @staticmethod
  def append_to_string(text, string):
    result = text
    if len(result) > 1:
      result = u'{0},{1}'.format(result, string)
    else:
      result = u'{0}{1}'.format(result, string)
    return result

  def to_dict(self):
    return {'disabled': self.disabled,
            'priviledged': self.privileged,
            'set_group': self.set_group,
            'validate': self.validate}

  def populate(self, json):
    self.privileged = json.get('priviledged', False)
    self.disabled = json.get('disabled', False)
    self.set_group = json.get('set_group', False)
    self.validate = json.get('validate', False)


class User(Base):
  name = Column('name', Unicode(255), nullable=False)
  sirname = Column('sirname', Unicode(255), nullable=False)
  username = Column('username', Unicode(255), nullable=False, unique=True)
  password = Column('password', Unicode(255), nullable=False)
  last_login = Column('last_login', DateTime)
  email = Column('email', Unicode(255), unique=True)
  api_key = Column('apikey', Unicode(255))
  gpg_key = Column('gpg_key', Text)
  activated = Column('activated', DateTime)
  activation_sent = Column('activation_sent', DateTime)
  activation_str = Column('activation_str', Unicode(255))
  dbcode = Column('code', Integer, default=0, nullable=False)
  __bit_code = None
  group_id = Column('group_id', Unicode(45), ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), index=True)
  group = relationship(Group, backref='users')
  plain_password = None

  @property
  def can_access(self):
    return (not self.permissions.disabled) and self.is_activated

  @property
  def is_activated(self):
    return self.activated and self.activation_str is None

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
    # TODO: Verify validation of User Object
    if not (self.password or self.username):
      return False
    ObjectValidator.validateAlNum(self,
                                  'username',
                                  minLength=3,
                                  maxLength=254)
    # Don't update if the password is already a hash
    if not (self.password == 'EXTERNALAUTH') and re.match('^[0-9a-f]{40}$',
                                                          self.password) is None:
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

  def to_dict(self, complete=True):
    if complete:
      return {'identifier': self.convert_value(self.identifier),
              'name': self.convert_value(self.name),
              'activated': self.convert_value(self.activated),
              'activation_send': self.convert_value(self.activation_sent),
              'activation_str': self.convert_value(self.activation_str),
              'api_key': self.convert_value(self.api_key),
              'dbcode': self.convert_value(self.dbcode),
              'email': self.convert_value(self.email),
              'gpg_key': self.convert_value(self.gpg_key),
              'group_id': self.convert_value(self.group_id),
              'permissions': self.permissions.to_dict(),
              # TODO: add group to dict fct
              'group': None,
              'last_login': self.convert_value(self.last_login),
              'password': self.convert_value(self.password),
              'sirname': self.convert_value(self.sirname),
              'username': self.convert_value(self.username)
              }
    else:
      return {'identifier': self.identifier,
              'username': self.username
              }

  def populate(self, json):
    self.name = json.get('name', None)
    self.email = json.get('email', None)
    self.gpg_key = json.get('gpg_key', None)
    self.api_key = json.get('api_key', None)
    self.sirname = json.get('sirname', None)
    self.username = json.get('username', None)
    group_id = json.get('group_id', None)
    if group_id:
      self.group_id = group_id
    else:
      self.group_id = None
    self.plain_password = json.get('password', None)
    # permissions setting
    self.permissions.populate(json.get('permissions', {}))
    # TODO add group
