"""module for session handling and brokers"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.interfaces import PoolListener
from ce1sus.db.broker import BrokerBase
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from ce1sus.helpers.config import Configuration
import os
import socket
from ce1sus.helpers.debug import Log


BASE = declarative_base()

class SessionManagerException(Exception):
  """sessionClazz Manager Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)

class BrokerInstantiationException(Exception):
  """Broker Instantiation Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)

class ForeignKeysListener(PoolListener):
  """
  Foreign Key listener to set the foreign_keys
  """
  def connect(self, dbapi_connection, connection_record):
    """
    overridden method of PoolListener
    """
    db_cursor = dbapi_connection.execute('pragma foreign_keys=ON')
    db_cursor.close()

class SessionManager:
  """
  sessionClazz manager for the session handling
  """

  def __init__(self, configFile):
    SessionManager.instance = self

    # load __config foo!!

    self.__config = Configuration(configFile, 'SessionManager')


    # setup connection string and engine
    protocol = self.__config.get('protocol')
    debug = self.__config.get('debug')

    if debug == None:
      debug = False
    if (protocol == 'sqlite'):
      connetionString = '{prot}:///../../../{db}'.format(prot=protocol,
                                                  db=self.__config.get('db'))
      # setup the engine
      self.engine = create_engine(connetionString,
                                listeners=[ForeignKeysListener()], echo=debug)
    else:
      hostname = self.__config.get('host')
      port = self.__config.get('port')
      # check if host is available
      response = os.system("ping -c 1 " + hostname)
      if response != 0:
        raise SessionManagerException('Host "{hostname}" not ' +
                                      'available'.format(hostname=hostname))

      # check if socket available
      if not SessionManager.isServiceExisting(hostname, port):
        raise SessionManagerException('Service on "{hostname}:{port}"' +
                                      ' not available'.format(hostname=hostname,
                                                               port=port))

      connetionString = '{prot}://{user}:{password}@{host}:{port}/{db}'.format(
        prot=protocol,
        user=self.__config.get('username'),
        password=self.__config.get('password'),
        host=hostname,
        db=self.__config.get('db'),
        port=port
      )
      self.engine = create_engine(connetionString, echo=debug)

    # setup sessionClazz
    # Get session class
    self.sessionClazz = scoped_session(sessionmaker(bind=self.engine,
                                            autocommit=False, autoflush=False))
    # instantiate session
    self.session = self.sessionClazz()


  @staticmethod
  def isServiceExisting(host, port):
    """
    Checks if the service port on the host is opened

    :returns: Boolean
    """
    captive_dns_addr = ""
    host_addr = ""

    try:
      host_addr = socket.gethostbyname(host)

      if (captive_dns_addr == host_addr):
        return False

      s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      s.settimeout(1)
      s.connect((host, port))
      s.close()
    except socket.error as e:
      Log.getLogger("SessionManager").info(e)
      return False

    return True


  def getEngine(self):
    """
    Returns the session engine

    :returns: Session
    """
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
        raise BrokerInstantiationException('Class does not ' +
                                           'implement BrokerBase')

      broker = clazz(self.session)
      return broker
    except Exception as e:
      self.getLogger().critical(e)
      raise IndentationError('Could not instantiate broker ' + clazz.__name__)

  def close(self):
    """
    Closes the session
    """
    pass

  @staticmethod
  def getInstance():
    """
    Returns the instance (Singleton pattern)


    :returns: SessionManager
    """
    if SessionManager.instance == None:
      raise IndentationError('No SessionManager present')
    return SessionManager.instance

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Log.getLogger(self.__class__.__name__)
