# -*- coding: utf-8 -*-

"""
The base module for brokers

Created Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


import sqlalchemy.orm.exc
from abc import ABCMeta, abstractmethod
from dagr.helpers.debug import Log

class BrokerException(Exception):
  """Broker Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)

class IntegrityException(BrokerException):
  """Broker Exception"""
  def __init__(self, message):
    BrokerException.__init__(self, message)

class InstantiationException(BrokerException):
  """Instantiation Exception"""

  def __init__(self, message):
    BrokerException.__init__(self, message)

class NothingFoundException(BrokerException):
  """NothingFound Exception"""
  def __init__(self, message):
    BrokerException.__init__(self, message)

class TooManyResultsFoundException(BrokerException):
  """Too many results found Exception"""
  def __init__(self, message):
    BrokerException.__init__(self, message)

class ValidationException(BrokerException):
  """Invalid Exception"""
  def __init__(self, message):
    BrokerException.__init__(self, message)

class OperationException(BrokerException):
  """Operation Exception"""
  def __init__(self, message):
    BrokerException.__init__(self, message)

class DeletionException(BrokerException):
  """
  Deletion Exception
  """
  def __init__(self, message):
    BrokerException.__init__(self, message)

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
  def getBrokerClass(self):
    """
    Returns the used class

    :returns: Class
    """
    return self.__class__

  @staticmethod
  def __objectToDictionary(obj):
    """
    Transforms the public/protected
    attributes of an object to a dictionary

    :param object: the object to be converted

    :returns: Dictionary
    """
    dictionary = dict()
    for name, value in vars(type(obj)).iteritems():
      # detect
      if hasattr(value, 'property'):
        prop = getattr(value, 'property')
        if hasattr(prop, 'columns'):
          columns = getattr(prop, 'columns')

          if len(columns) == 1:
            for column in columns:
              columnName = column.name
              # getRealValue
              # Primary keys cannot be updated!!
              if (hasattr(obj, name)) and not column.primary_key:
                instanceValue = getattr(obj, name)
                dictionary.update({columnName:instanceValue})
    return dictionary

  def getByID(self, identifier):
    """
    Returns the object by the given identifier

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :param identifier: the id of the requested user object
    :type identifier: integer

    :returns: Object
    """
    try:

      result = self.session.query(self.getBrokerClass()).filter(
                        getattr(self.getBrokerClass(),
                                'identifier') == identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with ID :{0}'.format(
                                                                  identifier))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException(
                    'Too many results found for ID :{0}'.format(identifier))
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result

  def getAll(self):
    """
    Returns all getBrokerClass() instances

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :returns: list of instances
    """
    try:
      result = self.session.query(self.getBrokerClass()).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result

  def removeByID(self, identifier, commit=True):
    """
    Removes the <<getBrokerClass()>> with the given identifier

    :param identifier:  the id of the requested user object
    :type identifier: integer
    """
    try:
      self.session.query(self.getBrokerClass()).filter(
                      getattr(self.getBrokerClass(),
                                'identifier') == identifier
                      ).delete(synchronize_session='fetch')

    except sqlalchemy.exc.OperationalError as e:
      self.session.rollback()
      raise OperationException(e)
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

    self.doCommit(commit)


  def doCommit(self, commit=True):
    """
    General commit, or rollback in case of an esception

    :param commit: If set a commit is done else a flush
    :type commit: Boolean
    """

    try:
      if commit:
        self.session.commit()
      else:
        self.session.flush()
    except sqlalchemy.exc.IntegrityError as e:
      self.session.rollback()
      self.getLogger().critical(e)
      raise IntegrityException(e)
    except sqlalchemy.exc.DatabaseError as e:
      self.session.rollback()
      self.getLogger().fatal(e)
      raise BrokerException(e)
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)
    finally:
      if commit:
        self.session.remove()


  def insert(self, instance, commit=True):
    """
    Insert a <<getBrokerClass()>>

    :param instance: The getBrokerClass() to be inserted
    :type instance: extension of Base

    Note: handles the commit and the identifier of the user is taken
           into account if set
    """
    errors = not instance.validate()
    if errors:
      raise ValidationException('Instance to be inserted is invalid')
    try:
      self.session.add(instance)
      self.doCommit(commit)
    except sqlalchemy.exc.IntegrityError as e:
      self.getLogger().critical(e)
      raise IntegrityException(e)


    except sqlalchemy.exc.DatabaseError as e:
      self.getLogger().error(e)
      self.session.rollback()
      raise BrokerException(e)

    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)



  def update(self, instance, commit=True):
    """
    updates an <<getBrokerClass()>>

    :param instance: The getBrokerClass() to be updated
    :type instance: extension of Base

    """
    errors = not instance.validate()
    if errors:
      raise ValidationException('Instance to be inserted is invalid')
    # an elo den update
    try:
      self.session.merge(instance)
    except sqlalchemy.exc.IntegrityError as e:
      self.getLogger().critical(e)
      raise IntegrityException(e)

    except sqlalchemy.exc.DatabaseError as e:
      self.getLogger().error(e)
      self.session.rollback()
      raise BrokerException(e)

    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

    self.doCommit(commit)

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Log.getLogger(self.__class__.__name__)



