# -*- coding: utf-8 -*-

"""
module for session handling and brokers

Created Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from sqlalchemy.interfaces import PoolListener
from c17Works.db.broker import BrokerBase
from c17Works.helpers.config import Configuration
import os
import socket
from c17Works.helpers.debug import Log
from cherrypy.process import plugins
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import cherrypy

BASE = declarative_base()

class SessionManagerException(Exception):
  """sessionClazz Manager Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)

class BrokerInstantiationException(Exception):
  """Broker Instantiation Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)

class SAEnginePlugin(plugins.SimplePlugin):
  """The SAEnglinge
  Original found under
  http://www.defuze.org/archives/222-integrating-
                                    sqlalchemy-into-a-cherrypy-application.html
  """

  def __init__(self, bus, connectionString, addListener=False, debug=False):
    """
    The plugin is registered to the CherryPy engine and therefore
    is part of the bus (the engine *is* a bus) registery.

    We use this plugin to create the SA engine. At the same time,
    when the plugin starts we create the tables into the database
    using the mapped class of the global metadata.

    Finally we create a new 'bind' channel that the SA tool
    will use to map a session to the SA engine at request time.
    """
    plugins.SimplePlugin.__init__(self, bus)
    self.sa_engine = None
    self.bus.subscribe("bind", self.bind)
    self.listener = addListener
    self.debug = debug
    self.connectionString = connectionString

  def start(self):
    """Start the engine"""
    if self.listener:
      self.sa_engine = create_engine(self.connectionString,
                            listeners=[ForeignKeysListener()],
                            echo=self.debug)
    else:
      self.sa_engine = create_engine(self.connectionString,
                            echo=self.debug)


  def stop(self):
    """stops the engine"""
    if self.sa_engine:
      self.sa_engine.dispose()
      self.sa_engine = None

  def bind(self, session):
    """binds the engine"""
    session.configure(bind=self.sa_engine)

  def getEngine(self):
    """returns the engine"""
    return self.sa_engine


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

class SATool(cherrypy.Tool):
  """The SATool
  Original found under
  http://www.defuze.org/archives/222-integrating-
                                    sqlalchemy-into-a-cherrypy-application.html
  """
  def __init__(self):
    """
    The SA tool is responsible for associating a SA session
    to the SA engine and attaching it to the current request.
    Since we are running in a multithreaded application,
    we use the scoped_session that will create a session
    on a per thread basis so that you don't worry about
    concurrency on the session object itself.

    This tools binds a session to the engine each time
    a requests starts and commits/rollbacks whenever
    the request terminates.
    """
    cherrypy.Tool.__init__(self, 'on_start_resource',
                           self.bind_session,
                           priority=20)

    self.session = scoped_session(sessionmaker(autoflush=False,
                                               autocommit=False))

  def _setup(self):
    cherrypy.Tool._setup(self)
    cherrypy.request.hooks.attach('on_end_resource',
                                  self.commit_transaction,
                                  priority=80)

  def bind_session(self):
    """Binds the session"""
    cherrypy.engine.publish('bind', self.session)
    cherrypy.request.db = self.session

  def commit_transaction(self):
    """Commit transaction"""
    cherrypy.request.db = None
    try:
      function = getattr(self.session, 'commit')
      function()
    except:
      function = getattr(self.session, 'rollback')
      function()
      raise
    finally:
      self.session.remove()

  def getSession(self):
    """Returns the session"""
    return self.session

class SessionManager:
  """
  sessionClazz manager for the session handling
  """
  instance = None

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
      SAEnginePlugin(cherrypy.engine, connetionString, True, debug).subscribe()
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
      SAEnginePlugin(cherrypy.engine, connetionString, False, debug).subscribe()
    # session setup
    self.saTool = SATool()
    cherrypy.tools.db = self.saTool

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
    return self.saTool.getSession()

  def brokerFactory(self, clazz):
    """
    Creates and initializes a broker

    :param clazz: broker class
    :type clazz: extension of BrokerBase

    :returns: instance of a Broker
    """
    if not issubclass(clazz, BrokerBase):
      raise BrokerInstantiationException('Class does not ' +
                                         'implement BrokerBase')

    broker = clazz(self.getEngine())
    return broker

  def close(self):
    """
    Closes the session
    """
    pass

  @classmethod
  def getInstance(cls):
    """
    Returns the instance (Singleton pattern)

    :returns: SessionManager
    """
    if SessionManager.instance is None:
      raise IndentationError('No SessionManager present')
    return SessionManager.instance

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Log.getLogger(self.__class__.__name__)
