"""This module provides container classes and interfaces
for inserting data into the database.
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 4, 2013


from ce1sus.db.broker import BrokerBase, NothingFoundException, \
ValidationException, TooManyResultsFoundException
import sqlalchemy.orm.exc
import hashlib
from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from ce1sus.db.session import BASE
import ce1sus.helpers.validator as validator
import re

# Relation table for user and groups

# ass net agebonnen mai ouni geet et net!?
__REL_USER_GROUPS = Table(
    'User_has_Groups', BASE.metadata,
    Column('user_id', Integer, ForeignKey('Users.user_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
    )

class User(BASE):
  """This is a container class for the USERS table."""
  __tablename__ = 'Users'

  identifier = Column('user_id', Integer, primary_key=True)
  username = Column('username', String)
  password = Column('password', String)
  privileged = Column('privileged', Integer)
  last_login = Column('last_login', DateTime)
  email = Column('email', String)

  groups = relationship('Group', secondary='User_has_Groups',
                        back_populates='users', cascade='all')

  def addGroup(self, group):
    """
    Add a group to this user

    :param group: Group to be added
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Group to be added is invalid')
    self.groups.append(group)

  def removeGroup(self, group):
    """
    Remove a group to this user

    :param group: Group to be removes
    :type group: Group
    """
    errors = not group.validate()
    if errors:
      raise ValidationException('Group to be removed is invalid')
    self.groups.remove(group)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    validator.validateAlNum(self, 'username')
    # TODO: find a way to validate password earlier!
    # validator.validateRegex(self, 'password', "(?=^.{8,}$)(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9])(?=.*[\W_])(?=^.*[^\s].*$).*$", 'Password has to be set and contain Upper/Lower cases, symbols and numbers and have at least a length of 8')
    validator.validateRegex(self, 'privileged', "^[01]+$", 'Privileged has to be set.')
    validator.validateEmailAddress(self, 'email')
    return validator.isObjectValid(self)

class Group(BASE):
  """This is a container class for the GRUOPS table."""
  __tablename__ = 'Groups'

  identifier = Column('group_id', Integer, primary_key=True)
  name = Column('name', String)
  shareTLP = Column('auto_share_tlp', Integer)
  description = Column('description', String)
  users = relationship(User, secondary='User_has_Groups',
                       back_populates='groups', cascade='all')


  def __str__(self):
    return str(self.__dict__)

  def addUser(self, user):
    """
    Add a user to this group

    :param user: User to be added
    :type user: User
    """
    errors = not user.validate()
    if errors:
      raise ValidationException('User to be added is invalid')
    self.users.append(user)

  def removeUser(self, user):
    """
    Remove a user to this group

    :param user: User to be removes
    :type user: User
    """
    errors = not user.validate()
    if errors:
      raise ValidationException('User to be removed is invalid')
    self.users.remove(user)

  def validate(self):
    """
    Checks if the attributes of the class are valid

    :returns: Boolean
    """
    validator.validateAlNum(self, 'name')
    validator.validateDigits(self, 'shareTLP')
    return validator.isObjectValid(self)


class GroupBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Group

  def getUsersByGroup(self, identifier, belongIn=True):
    """
    get all users in a given group

    :param identifier: identifier of the group
    :type identifier: Integer
    :param belongIn: If set returns all the attributes of the object else
                     all the attributes not belonging to the object
    :type belongIn: Boolean

    :returns: list of Users
    """
    try:
      users = self.session.query(User).join(Group.users).filter(
                                        Group.identifier == identifier).all()
      if not belongIn:
        userIDs = list()
        for user in users:
          userIDs.append(user.identifier)
        users = self.session.query(User).filter(~User.identifier.in_(
                                                                    userIDs))
    except sqlalchemy.orm.exc.NoResultFound:
      users = list()
    return users

  def addGroupToUser(self, userID, groupID, commit=True):
    """
    Add a user to a group

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    group.addUser(user)
    if commit:
      self.session.commit()
    else:
      self.session.flush()

  def removeGroupFromUser(self, userID, groupID, commit=True):
    """
    Removes a user to a group

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    group.removeUser(user)
    if commit:
      self.session.commit()
    else:
      self.session.flush()



class UserBroker(BrokerBase):
  """This is the interface between python an the database"""


  @staticmethod
  def __hashPassword(password, salt):
    """
    Returns hashed password
    """
    if not password or password is None:
      return ''

    if password == 'EXTERNALAUTH':
      return password


    hashedPwd = hashlib.sha1()
    hashedPwd.update(password + salt)
    return hashedPwd.hexdigest()


  def insert(self, instance, commit=True):
    """
    overrides BrokerBase.insert
    """
    instance.password = self.__hashPassword(instance.password,
                                             instance.username)

    errors = not instance.validate()
    if errors:
      raise ValidationException('User to be inserted is invalid')
    BrokerBase.insert(self, instance, commit)

  def update(self, instance, commit=True):
    """
    overrides BrokerBase.insert
    """
    # Don't update if the password is already a hash
    if re.match('^[0-9a-f]{40}$', instance.password) is None:
      instance.password = self.__hashPassword(instance.password,
                                             instance.username)

    errors = not instance.validate()
    if errors:
      raise ValidationException('User to be inserted is invalid')
    BrokerBase.update(self, instance, commit)

  def isUserPrivileged(self, username):
    """
    Checks if the user has the privileged flag set

    :returns: Boolean
    """
    user = self.getUserByUserName(username)
    if (user.privileged == 1):
      return True
    else:
      return False

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return User

  def getUserByUserName(self, username):
    """
    Returns the user with the following username

    :param user: The username
    :type user: Stirng

    :returns: User
    """
    try:
      user = self.session.query(User).filter(User.username == username).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(username))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for' +
                                         'ID :{0}'.format(username))
    return user

  def getUserByUsernameAndPassword(self, username, password):
    """
    Returns the user with the following username and password

    Note: Password will be hashed inside this function

    :param user: The username
    :type user: Stirng
    :param password: The username
    :type password: Stirng

    :returns: User
    """
    passwd = self.__hashPassword(password, username)
    try:
      user = self.session.query(User).filter(User.username == username,
                                             User.password == passwd).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(username))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID ' +
                                         ':{0}'.format(username))
    return user

  def getGroupsByUser(self, identifier, belongIn=True):
    """
    Returns the groups of the given user

    Note: Password will be hashed inside this function

    :param identifier: identifier of the user
    :type identifier: Integer
    :param belongIn: If set returns all the groups of the user else
                     all the groups not belonging to the user
    :type belongIn: Boolean

    :returns: list of Users

    :returns: User
    """
    try:
      groups = self.session.query(Group).join(User.groups).filter(
                                          User.identifier == identifier).all()
      if not belongIn:
        groupIDs = list()
        for group in groups:
          groupIDs.append(group.identifier)
        groups = self.session.query(Group).filter(~Group.identifier.in_(
                                                                    groupIDs))
    except sqlalchemy.orm.exc.NoResultFound:
      groups = list()
    return groups

  def addUserToGroup(self, userID, groupID, commit=True):
    """
    Add a group to a user

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    user.addGroup(group)
    if commit:
      self.session.commit()
    else:
      self.session.flush()

  def removeUserFromGroup(self, userID, groupID, commit=True):
    """
    removes a group to a user

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    user.removeGroup(group)
    if commit:
      self.session.commit()
    else:
      self.session.flush()


