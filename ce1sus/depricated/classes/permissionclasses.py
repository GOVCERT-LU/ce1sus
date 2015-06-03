# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""
import re
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime

from ce1sus.db.common.session import BaseClass
from ce1sus.depricated.brokers.basefoo import BASE
from ce1sus.depricated.helpers.bitdecoder import BitRight
from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# Relation table for user and groups, ass net agebonnen mai ouni geet et net!?
__REL_SUBGROUP_GROUPS = Table('Subgroups_has_Groups', getattr(BASE, 'metadata'),
                              Column('subgroup_id', Integer, ForeignKey('Subgroups.subgroup_id')),
                              Column('group_id', Integer, ForeignKey('Groups.group_id')))


# pylint: disable=R0903
class OldUser(BASE):
    """This is a container class for the USERS table."""
    def __init__(self):
        pass

    def to_dict(self):
        subgroups = list()
        for subgroup in subgroups:
            subgroups.append(subgroup.to_dict())
        return {'identifier': BaseClass.convert_value(self.identifier),
                'username': BaseClass.convert_value(self.username),
                'password': BaseClass.convert_value(self.password),
                'last_login': BaseClass.convert_value(self.last_login),
                'email': BaseClass.convert_value(self.email),
                'disabled': BaseClass.convert_value(self.disabled),
                'api_key': BaseClass.convert_value(self.api_key),
                'gpg_key': BaseClass.convert_value(self.gpg_key),
                'group_id': BaseClass.convert_value(self.group_id),
                'activated': BaseClass.convert_value(self.activated),
                'activation_sent': BaseClass.convert_value(self.activation_sent),
                'name': BaseClass.convert_value(self.name),
                'sirname': BaseClass.convert_value(self.sirname),
                'activation_str': BaseClass.convert_value(self.activation_str),
                'dbcode': BaseClass.convert_value(self.dbcode)

                }

    __tablename__ = 'Users'
    identifier = Column('user_id', Integer, primary_key=True)
    username = Column('username', String)
    password = Column('password', String)
    last_login = Column('last_login', DateTime)
    email = Column('email', String)
    disabled = Column('disabled', Integer)
    api_key = Column('apikey', String)
    gpg_key = Column('gpg_key', String)
    group_id = Column('group_id', Integer, ForeignKey('Groups.group_id'))
    default_group = relationship('OldGroup',
                                 primaryjoin='OldUser.group_id==OldGroup.identifier',
                                 lazy='joined')
    activated = Column('activated', DateTime)
    activation_sent = Column('activation_sent', DateTime)
    name = Column('name', String)
    sirname = Column('sirname', String)
    password_plain = None
    activation_str = Column('activation_str', String)

    dbcode = Column('code', Integer)
    __bit_code = None

    @property
    def is_activated(self):
        return self.activated and self.activation_str is None

    @property
    def rights(self):
        """
        Property for the bit_value
        """
        if self.__bit_code is None:
            if self.dbcode is None:
                self.__bit_code = BitRight('0', self)
            else:
                self.__bit_code = BitRight(self.dbcode, self)
        return self.__bit_code

    @rights.setter
    def rights(self, bitvalue):
        """
        Property for the bit_value
        """
        self.__bit_code = bitvalue
        self.dbcode = bitvalue.bit_code

    @property
    def privileged(self):
        return self.rights.privileged

    @privileged.setter
    def privileged(self, value):
        if value:
            self.rights.privileged = True
        else:
            self.rights.privileged = False

    @property
    def display_name(self):
        return '{0} {1}'.format(self.sirname, self.name)

    @property
    def allowed(self):
        if self.disabled == 0 and self.activated:
            return True
        return False

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
                                          (r"(?=^.{8,}$)(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[\W_])(?=^.*[^\s].*$).*$"),
                                          ('Password has to be set and contain Upper and Lower cases, symbols and numbers and have at least a length of 8')
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


class OldGroup(BASE):
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
    subgroups = relationship('OldSubGroup',
                             secondary='Subgroups_has_Groups', cascade='all',
                             order_by="OldSubGroup.name",
                             lazy='joined')
    gpg_key = Column('gpg_key', String)
    uuid = Column('uuid', String)

    def to_dict(self):
        subgroups = list()
        for subgroup in subgroups:
            subgroups.append(subgroup.to_dict())
        return {'identifier': BaseClass.convert_value(self.identifier),
                'name': BaseClass.convert_value(self.name),
                'description': BaseClass.convert_value(self.description),
                'can_download': BaseClass.convert_value(self.can_download),
                'usermails': BaseClass.convert_value(self.usermails),
                'email': BaseClass.convert_value(self.email),
                'tlp_lvl': BaseClass.convert_value(self.tlp_lvl),
                'gpg_key': BaseClass.convert_value(self.gpg_key),
                'uuid': BaseClass.convert_value(self.uuid),
                }

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
        if self.usermails == 0:
            ObjectValidator.validateEmailAddress(self, 'email')
        return ObjectValidator.isObjectValid(self)


class OldSubGroup(BASE):
    """
    Sub group class
    """

    def __init__(self):
        pass

    __tablename__ = 'Subgroups'
    identifier = Column('subgroup_id', Integer, primary_key=True)
    name = Column('name', String)
    description = Column('description', String)
    groups = relationship(OldGroup,
                          secondary='Subgroups_has_Groups',
                          cascade='all',
                          order_by="OldGroup.name")

    def to_dict(self):
        subgroups = list()
        for subgroup in subgroups:
            subgroups.append(subgroup.to_dict())
        return {'identifier': BaseClass.convert_value(self.identifier),
                'name': BaseClass.convert_value(self.name),
                'description': BaseClass.convert_value(self.description),
                }

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
