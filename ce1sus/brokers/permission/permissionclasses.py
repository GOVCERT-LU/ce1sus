# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from dagr.db.broker import DateTime
from dagr.db.session import BASE
from dagr.helpers.validator.objectvalidator import ObjectValidator
import re

# Relation table for user and groups, ass net agebonnen mai ouni geet et net!?
__REL_SUBGROUP_GROUPS = Table(
   'Subgroups_has_Groups', getattr(BASE, 'metadata'),
   Column('subgroup_id', Integer, ForeignKey('Subgroups.subgroup_id')),
   Column('group_id', Integer, ForeignKey('Groups.group_id'))
   )


# pylint: disable=R0903
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
  disabled = Column('disabled', Integer)
  api_key = Column('apikey', String)
  group_id = Column('group_id', Integer, ForeignKey('Groups.group_id'))
  default_group = relationship('Group',
                              primaryjoin='User.group_id==Group.identifier',
                              lazy='joined')

  @property
  def has_api_key(self):
    """
    Returns true if the user has an api key
    """
    if self.api_key is None:
      return 0
    else:
      return 1

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


class Group(BASE):
  """This is a container class for the GRUOPS table."""
  def __init__(self):
    pass

  __tablename__ = 'Groups'
  identifier = Column('group_id', Integer, primary_key=True)
  name = Column('name', String)
  description = Column('description', String)
  can_download = Column('canDownlad', Integer)
  usermails = Column('usermails', Integer)
  email = Column('email', String)
  tlp_lvl = Column('tlplvl', Integer)
  subgroups = relationship('SubGroup', secondary='Subgroups_has_Groups',
                       back_populates='groups', cascade='all',
                            order_by="SubGroup.name",
                              lazy='joined')

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    ObjectValidator.validateAlNum(self, 'name',
                                  withSymbols=True,
                                  minLength=3)
    ObjectValidator.validateAlNum(self,
                                  'description',
                                  minLength=5,
                                  withSpaces=True,
                                  withNonPrintableCharacters=True,
                                  withSymbols=True)
    ObjectValidator.validateDigits(self, 'can_download', minimal=0, maximal=1)
    ObjectValidator.validateDigits(self, 'usermails', minimal=0, maximal=1)
    ObjectValidator.validateEmailAddress(self, 'email')
    return ObjectValidator.isObjectValid(self)


class SubGroup(BASE):
  """
  Sub group class
  """

  def __init__(self):
    pass

  __tablename__ = 'Subgroups'
  identifier = Column('subgroup_id', Integer, primary_key=True)
  name = Column('name', String)
  description = Column('description', String)
  groups = relationship(Group, secondary='Subgroups_has_Groups',
                       back_populates='subgroups', cascade='all',
                            order_by="Group.name")

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
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
