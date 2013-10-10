# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import ValidationException
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from dagr.db.session import BASE
from dagr.helpers.validator.objectvalidator import ObjectValidator
import re

# Relation table for user and groups, ass net agebonnen mai ouni geet et net!?
__REL_USER_GROUPS = Table(
   'User_has_Groups', BASE.metadata,
   Column('user_id', Integer, ForeignKey('Users.user_id')),
   Column('group_id', Integer, ForeignKey('Groups.group_id'))
   )


class User(BASE):
  """This is a container class for the USERS table."""
  def __init__(self):
    pass

  __tablename__ = 'Users'
  identifier = Column('user_id', Integer, primary_key=True)
  username = Column('username', String)
  password = Column('password', String)
  privileged = Column('privileged', Integer)
  last_login = Column('last_login', DateTime)
  email = Column('email', String)
  groups = relationship('Group', secondary='User_has_Groups',
                        back_populates='users', cascade='all')
  disabled = Column('disabled', Integer)
  apiKey = Column('apikey', Integer)

  def addGroup(self, group):
    """
    Add a group to this user

    :param group: Group to be added
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Group to be added is invalid')
    function = getattr(self.groups, 'append')
    function(group)

  def removeGroup(self, group):
    """
    Remove a group to this user

    :param group: Group to be removes
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Group to be removed is invalid')
    function = getattr(self.groups, 'remove')
    function(group)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self, 'username', minLength=3)
    # Don't update if the password is already a hash
    if not (self.password == 'EXTERNALAUTH') and re.match('^[0-9a-f]{40}$',
                                                        self.password) is None:
      ObjectValidator.validateRegex(self,
                                'password',
                                (r"(?=^.{8,}$)(?=.*[a-z])(?=.*[A-Z])"
                                + r"(?=.*[0-9])(?=.*[\W_])(?=^.*[^\s].*$).*$"),
                                ('Password has to be set and contain Upper and'
                                + 'Lower cases, symbols and numbers and have'
                                + ' at least a length of 8'))
    ObjectValidator.validateDigits(self, 'privileged', minimal=0, maximal=1)
    ObjectValidator.validateDigits(self, 'disabled', minimal=0, maximal=1)
    ObjectValidator.validateEmailAddress(self, 'email')
    if not self.last_login is None:
      ObjectValidator.validateDateTime(self, 'last_login')
    return ObjectValidator.isObjectValid(self)

  def toDict(self, full=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['identifier'] = self.identifier
    result[self.__class__.__name__]['username'] = self.username
    result[self.__class__.__name__]['email'] = self.email
    return result


class Group(BASE):
  """This is a container class for the GRUOPS table."""
  def __init__(self):
    pass

  __tablename__ = 'Groups'
  identifier = Column('group_id', Integer, primary_key=True)
  name = Column('name', String)
  shareTLP = Column('auto_share_tlp', Integer)
  description = Column('description', String)
  canDownload = Column('canDownlad', Integer)
  users = relationship(User, secondary='User_has_Groups',
                       back_populates='groups', cascade='all')
  tlpLvl = Column('tlplvl', Integer)

  def __str__(self):
    return unicode(self.__dict__)

  def addUser(self, user):
    """
    Add a user to this group

    :param user: User to be added
    :type user: User
    """
    errors = not user.validate()
    if errors:
      raise ValidationException('User to be added is invalid')
    function = getattr(self.users, 'append')
    function(user)

  def removeUser(self, user):
    """
    Remove a user to this group

    :param user: User to be removes
    :type user: User
    """
    errors = not user.validate()
    if errors:
      raise ValidationException('User to be removed is invalid')
    function = getattr(self.users, 'remove')
    function(user)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self, 'name',
                                  withSymbols=True,
                                  minLength=3)
    ObjectValidator.validateDigits(self, 'shareTLP')
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  minLength=5,
                                  withSpaces=True,
                                  withNonPrintableCharacters=True,
                                  withSymbols=True)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  withNonPrintableCharacters=True,
                                  withSpaces=True,
                                  minLength=3,
                                  withSymbols=True)
    return ObjectValidator.isObjectValid(self)

  def toDict(self, full=False):
    result = dict()
    result[self.__class__.__name__] = dict()
    result[self.__class__.__name__]['identifier'] = self.identifier
    result[self.__class__.__name__]['name'] = self.name
    result[self.__class__.__name__]['description'] = self.description
    result[self.__class__.__name__]['shareTLP'] = self.shareTLP
    result[self.__class__.__name__]['canDownload'] = self.canDownload
    result[self.__class__.__name__]['tlpLvl'] = self.tlpLvl
    return result
