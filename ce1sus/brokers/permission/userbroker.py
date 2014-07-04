# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, \
ValidationException, TooManyResultsFoundException
import sqlalchemy.orm.exc
import dagr.helpers.hash as hasher
from dagr.db.broker import BrokerException
import re
from ce1sus.brokers.permission.permissionclasses import User, Group
from sqlalchemy.orm import joinedload


class UserBroker(BrokerBase):
  """This is the interface between python an the database"""

  def insert(self, instance, commit=True, validate=True):
    """
    overrides BrokerBase.insert
    """
    errors = False
    if validate:
      errors = not instance.validate()
      if errors:
        raise ValidationException(u'User to be inserted is invalid')
    if validate and not errors:
      instance.password = hasher.hashSHA1(instance.password,
                                             instance.username)

    try:
      BrokerBase.insert(self, instance, commit, validate=False)
      self.do_commit(commit)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def update(self, instance, commit=True):
    """
    overrides BrokerBase.insert
    """

    errors = not instance.validate()
    if errors:
      raise ValidationException(u'User to be updated is invalid')

    if instance.password != 'EXTERNALAUTH':
    # Don't update if the password is already a hash
      if re.match('^[0-9a-f]{40}$', instance.password) is None:
        if not errors:
          instance.password = hasher.hashSHA1(instance.password,
                                               instance.username)
    try:
      BrokerBase.update(self, instance, commit, validate=False)
      self.do_commit(commit)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

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

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
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
      raise NothingFoundException(u'Nothing found with ID :{0}'.format(username)
                                  )
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(u'Too many results found for' +
                                         'ID :{0}'.format(username))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
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
    if password == 'EXTERNALAUTH':
      passwd = password
    else:
      passwd = hasher.hashSHA1(password, username)

    try:
      user = self.session.query(User).options(joinedload(User.default_group, Group.subgroups)).filter(User.username == username,
                                             User.password == passwd).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found with ID :{0}'.format(username)
                                  )
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(u'Too many results found for ID ' +
                                         ':{0}'.format(username))
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)
    return user

  def get_user_by_api_key(self, api_key):
    # check if api key exists
    try:
      result = self.session.query(User).filter(
                       User.api_key == api_key).one()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found with apikey :{0}'.format(
                                                                  api_key))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for apikey :{0}'.format(api_key))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_all(self):
    """
    Returns all get_broker_class() instances

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :returns: list of instances
    """
    try:
      result = self.session.query(self.get_broker_class()
                                  ).order_by(User.username.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    return result

  def get_user_by_act_str(self, activation_str):
    try:
      result = self.session.query(User).filter(
                       User.activation_str == activation_str).one()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Nothing found for activation_str {0}'.format(activation_str))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for activation_str :{0}'.format(activation_str))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)
