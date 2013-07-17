from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.interfaces import PoolListener
from ce1sus.db.broker import BrokerBase
import ConfigParser
import os
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ce1sus.helpers.config import Configuration


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

Base = declarative_base()

class BrokerInstantiationException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

class ForeignKeysListener(PoolListener):
  """
  Foreign Key listener to set the foreign_keys
  """
  def connect(self, dbapi_connection, connection_record):
    db_cursor = dbapi_connection.execute('pragma foreign_keys=ON')
    db_cursor.close();

class SessionManager:
  """
  Session manager for the session handling
  """

  def __init__(self, configFile):
    SessionManager.instance = self

    # load __config foo!!

    self.__config = Configuration(configFile,'SessionManager')


    # setup connection string and engine
    protocol = self.__config.get('protocol')
    debug = self.__config.get('debug')

    if debug == None:
      debug = False
    if (protocol == 'sqlite'):
      connetionString = '{prot}:///../../../{db}'.format(prot=protocol, db=self.__config.get('db'))
      # setup the engine
      self.engine = create_engine(connetionString, listeners=[ForeignKeysListener()], echo=debug)
    else:
      connetionString = '{prot}://{user}:{password}@{host}:{port}/{db}'.format(
        prot=protocol,
        user=self.__config.get('username'),
        password=self.__config.get('password'),
        host=self.__config.get('host'),
        db=self.__config.get('db'),
        port=self.__config.get('port')
      )
      self.engine = create_engine(connetionString, echo=debug)

    # setup Session
    # Get session class
    self.Session = scoped_session(sessionmaker(bind=self.engine, autocommit=False, autoflush=False))
    # instantiate session
    self.session = self.Session()



    # self.Session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=self.engine))
    # self.Base = declarative_base(bind=self.engine)
    # self.session = self.Session()

  def getEngine(self):
    return self.session


  def brokerFactory(self, clazz):
    """
    Creates and initializes a broker
    
    :param clazz: broker class
    :type clazz: extension of BrokerBase
    
    :returns: instance of a Broker
    """
    # Instantiate broker
    try:

      if not issubclass(clazz, BrokerBase):
        raise BrokerInstantiationException('Class does not implement BrokerBase');

      broker = clazz(self.session)
      return broker
    except Exception:
      raise IndentationError('Could not instantiate broker ' + clazz.__name__)

  def close(self):
    pass

  @staticmethod
  def getInstance():
    if SessionManager.instance == None:
      raise IndentationError('No SessionManager present')
    return SessionManager.instance

