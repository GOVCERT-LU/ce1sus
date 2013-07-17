
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'



# Created on Jul 4, 2013


import sqlalchemy.orm.exc
from ce1sus.db.dbexceptions import NothingFoundException, TooManyResultsFoundException
from abc import ABCMeta, abstractmethod


class BrokerBase(object):

  __metaclass__ = ABCMeta

  def __init__(self, session):
    self.session = session
    self.clazz = None

  @abstractmethod
  def getBrokerClass(self):
    """
    Returns the used class
    
    :returns: Class
    """
    return

  def __objectToDictionary(self, obj):
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
              if (hasattr(obj, name)):
                instanceValue = getattr(obj, name)
                dictionary.update({columnName:instanceValue})
    return dictionary

  def getByID(self, identifier):
    """
    Returns the getBrokerClass() instance with the given identifier
    
    Note: raises a NothingFoundException or a TooManyResultsFound Exception
    
    :param identifier: the id of the requested user object
    :type identifier: integer
    
    :returns: getBrokerClass()
    """
    try:

      result = self.session.query(self.getBrokerClass()).filter(self.getBrokerClass().identifier == identifier).one()

    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('No attribute found with ID :{0}'.format(identifier))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for ID :{0}'.format(identifier))

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
    return result

  def removeByID(self, identifier):
    """
    Removes the <<getBrokerClass()>> with the given identifier
    
    :param identifier:  the id of the requested user object
    :type identifier: integer
    """
    self.session.query(self.getBrokerClass()).filter(self.getBrokerClass().identifier == identifier).delete(synchronize_session='fetch')
    self.session.commit()

  def insert(self, instance):
    """
    Insert a <<getBrokerClass()>>
    
    :param instance: The getBrokerClass() to be inserted
    :type instance: extension of Base
    
    Note: handles the commit and the identifier of the user is taken 
           into account if set
    """
    self.session.add(instance)
    self.session.commit()

  def update(self, instance):
    """
    updates an <<getBrokerClass()>>
    
    :param instance: The getBrokerClass() to be updated
    :type instance: extension of Base
    
    """
    dictionary = self.__objectToDictionary(instance)
    # an elo den update
    try:
      self.session.query(self.getBrokerClass()).filter(self.getBrokerClass().identifier == instance.identifier).update(dictionary);
      self.session.commit()
    except:
      self.session.rollback()


