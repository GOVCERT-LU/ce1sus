# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""
import re
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Column, ForeignKey, Table
from sqlalchemy.types import Unicode, Integer, Text, BIGINT

from ce1sus.db.common.broker import DateTime
from ce1sus.db.common.session import Base
from ce1sus.helpers.bitdecoder import BitBase
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


_REL_MAINGROUP_GROUPS = Table('group_has_associations', Base.metadata,
                              Column('gha_id', BIGINT, primary_key=True, nullable=False, index=True),
                              Column('association_id', BIGINT, ForeignKey('associations.association_id', onupdate='cascade', ondelete='cascade'), index=True),
                              Column('group_id', BIGINT, ForeignKey('groups.group_id', onupdate='cascade', ondelete='cascade'), index=True))


class GroupRights(BitBase):
  """
  The __bit_value is defined as follows:
  [0] : User is privileged
  [1] : User can validate
  [2] : User can set group via rest inserts
  """

  DOWNLOAD = 0

  @property
  def can_download(self):
    return self._get_value(GroupRights.DOWNLOAD)

  @can_download.setter
  def can_download(self, value):
    self._set_value(GroupRights.DOWNLOAD, value)


class UserRights(BitBase):

  """
  The __bit_value is defined as follows:
  [0] : User is privileged
  [1] : User can validate
  [2] : User can set group via rest inserts
  """

  PRIVILEGED = 0
  VALIDATE = 1
  SET_GROUP = 2

  @property
  def privileged(self):
    return self._get_value(UserRights.PRIVILEGED)

  @privileged.setter
  def privileged(self, value):
    self._set_value(UserRights.PRIVILEGED, value)

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
  association_id = Column('association_id', BIGINT, ForeignKey('associations.association_id', onupdate='restrict', ondelete='restrict'), index=True)
  association = relationship('Association', backref='users')

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

  @permissions.setter
  def permissions(self, bitvalue):
    """
    Property for the bit_value
    """
    self.__bit_code = bitvalue
    self.dbcode = bitvalue.bit_code

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

    ObjectValidator.validateDigits(self, 'disabled', minimal=0, maximal=1)
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


class Association(Base):
  name = Column('name', Unicode(255), nullable=False, unique=True)
  description = Column('description', Text)
  tlp_lvl = Column('tlplvl', Integer, default=4, nullable=False, index=True)
  dbcode = Column('code', Integer, default=0, nullable=False)
  __bit_code = None
  relationship('Group',
               secondary='group_has_associations',
               backref='groups',
               order_by='Group.name')

  @property
  def permissions(self):
    """
    Property for the bit_value
    """
    if self.__bit_code is None:
      if self.dbcode is None:
        self.__bit_code = GroupRights('0', self)
      else:
        self.__bit_code = GroupRights(self.dbcode, self)
    return self.__bit_code

  @permissions.setter
  def permissions(self, bitvalue):
    """
    Property for the bit_value
    """
    self.__bit_code = bitvalue
    self.dbcode = bitvalue.bit_code

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO: Verify validation of Group Object
    ObjectValidator.validateAlNum(self, 'name',
                                  withSymbols=True,
                                  minLength=3)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  minLength=5,
                                  withSpaces=True,
                                  withNonPrintableCharacters=True,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)


class Group(Base):
  name = Column('name', Unicode(255), nullable=False, unique=True)
  description = Column('description', Text)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    # TODO: Verify validation of Group Object
    ObjectValidator.validateAlNum(self, 'name',
                                  withSymbols=True,
                                  minLength=3)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  minLength=5,
                                  withSpaces=True,
                                  withNonPrintableCharacters=True,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)
