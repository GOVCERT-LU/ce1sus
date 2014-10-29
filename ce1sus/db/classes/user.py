# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 28, 2014
"""
import re
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy.types import Unicode, DateTime, Text, Integer, BIGINT

from ce1sus.db.classes.permissions import Group
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
    return self.activated or self.privileged or self.validate

  @property
  def privileged(self):
    return self._get_value(UserRights.PRIVILEGED)

  @privileged.setter
  def privileged(self, value):
    self._set_value(UserRights.PRIVILEGED, value)

  @property
  def activated(self):
    return self._get_value(UserRights.ACTIVATED)

  @activated.setter
  def activated(self, value):
    self._set_value(UserRights.ACTIVATED, value)

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
  group_id = Column('group_id', BIGINT, ForeignKey('groups.group_id', onupdate='restrict', ondelete='restrict'), index=True)
  group = relationship(Group, backref='users')

  @property
  def can_access(self):
    return self.permissions.activated and self.is_activated

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

    # ObjectValidator.validateEmailAddress(self, 'email')
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

  def to_dict(self):
    return {'name': self.convert_value(self.name),
            'activated': self.convert_value(self.activated),
            'activation_send': self.convert_value(self.activation_sent),
            'activation_str': self.convert_value(self.activation_str),
            'api_key': self.convert_value(self.api_key),
            'dbcode': self.convert_value(self.dbcode),
            'email': self.convert_value(self.email),
            'gpg_key': self.convert_value(self.gpg_key),
            'ĝroup_id': self.convert_value(self.group_id),
            # TODO: add group to dict fct
            'group': self.convert_value(None),
            'last_login': self.convert_value(self.last_login),
            # TODO: decide if you leave that in or only show EXTERNALAUT !?
            'password': self.convert_value(self.password),
            'sirname': self.convert_value(self.sirname),
            'username': self.convert_value(self.username),
            }
