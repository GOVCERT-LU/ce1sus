# -*- coding: utf-8 -*-

"""
The base module for brokers

Created Jul, 2013
"""
from abc import ABCMeta, abstractmethod
import dateutil
from sqlalchemy import DateTime as SdateTime
import sqlalchemy.orm.exc
from sqlalchemy.types import TypeDecorator

from ce1sus.helpers.common.validator.objectvalidator import ObjectValidator


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


# pylint: disable=W0223
class DateTime(TypeDecorator):
  """
  Used as workaround for MySQL DBs
  """
  impl = SdateTime

  def process_bind_param(self, value, engine):
    if engine:
      pass
    return value

  def process_result_value(self, value, engine):
    if engine:
      pass
    if value is None:
      return None
    else:
      return value.replace(tzinfo=dateutil.tz.tzutc())


class BrokerException(Exception):
  """Broker Exception"""
  pass


class IntegrityException(BrokerException):
  """Broker Exception"""
  pass


class InstantiationException(BrokerException):
  """Instantiation Exception"""
  pass


class NothingFoundException(BrokerException):
  """NothingFound Exception"""
  pass


class TooManyResultsFoundException(BrokerException):
  """Too many results found Exception"""
  pass


class ValidationException(BrokerException):
  """Invalid Exception"""
  pass


class DeletionException(BrokerException):
  """
  Deletion Exception
  """
  pass

# Created on Jul 4, 2013


class BrokerBase(object):
  """The base class for brokers providing the general methods"""
  __metaclass__ = ABCMeta

  def __init__(self, session):
    self.__session = session
    self.clazz = None
    self.identifier = None

  @property
  def session(self):
    """
    Returns the db session
    """
    return self.__session.session

  @abstractmethod
  def get_broker_class(self):
    """
    Returns the used class

    :returns: Class
    """
    return self.__class__

  def get_by_id(self, identifier):
    """
    Returns the object by the given identifier

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:

      result = self.session.query(self.get_broker_class()).filter(getattr(self.get_broker_class(),
                                                                          'identifier') == identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(identifier))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    return result

  def get_all(self, order=None):
    """
    Returns all get_broker_class() instances

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :returns: list of instances
    """
    try:
      result = self.session.query(self.get_broker_class())
      if order is not None:
        result = result.order_by(order)
      return result.all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

    return result

  def remove_by_id(self, identifier, commit=True):
    """
    Removes the <<get_broker_class()>> with the given identifier

    :param identifier:  the id of the requested user object
    :type identifier: integer
    """
    try:
      self.session.query(self.get_broker_class()).filter(getattr(self.get_broker_class(),
                                                                 'identifier') == identifier
                                                         ).delete(synchronize_session='fetch')
    except sqlalchemy.exc.IntegrityError as error:
      self.session.rollback()
      raise IntegrityException(error)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

    self.do_commit(commit)

  def do_rollback(self):
    """
    Performs a rollback
    """
    try:
      self.session.rollback()
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def do_commit(self, commit=True):
    """
    General commit, or rollback in case of an exception

    :param commit: If set a commit is done else a flush
    :type commit: Boolean
    """

    try:
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except sqlalchemy.exc.IntegrityError as error:
      self.session.rollback()
      raise IntegrityException(error)
    except sqlalchemy.exc.DatabaseError as error:
      self.session.rollback()
      raise BrokerException(error)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def insert(self, instance, commit=True, validate=True):
    """
    Insert a <<get_broker_class()>>

    :param instance: The get_broker_class() to be inserted
    :type instance: extension of Base

    Note: handles the commit and the identifier of the user is taken
           into account if set
    """
    if validate:
      errors = not instance.validate()
      if errors:
        raise ValidationException('Instance to be inserted is invalid.{0}'.format(ObjectValidator.getFirstValidationError(instance)))
    try:
      self.session.add(instance)
      self.do_commit(commit)
    except sqlalchemy.exc.IntegrityError as error:
      raise IntegrityException(error)
    except sqlalchemy.exc.DatabaseError as error:
      self.session.rollback()
      raise BrokerException(error)
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def update(self, instance, commit=True, validate=True):
    """
    updates an <<get_broker_class()>>

    :param instance: The get_broker_class() to be updated
    :type instance: extension of Base

    """
    if validate:
      errors = not instance.validate()
      if errors:
        raise ValidationException('Instance to be inserted is invalid.{0}'.format(ObjectValidator.getFirstValidationError(instance)))
    # an elo den update
    try:
      self.session.merge(instance)
      self.do_commit(commit)
    except sqlalchemy.exc.IntegrityError as error:
      raise IntegrityException(error)

    except sqlalchemy.exc.DatabaseError as error:
      self.session.rollback()
      raise BrokerException(error)

    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

    self.do_commit(commit)

  def clean_list(self, result):
    output = list()
    for item in result:
      output.append(item[0])
    return output
