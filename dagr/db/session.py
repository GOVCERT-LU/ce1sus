# -*- coding: utf-8 -*-

"""
module for session handling and brokers

Created Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase
from dagr.helpers.config import Configuration
from dagr.helpers.debug import Log
from sqlalchemy.ext.declarative import declarative_base
from dagr.db.connectors.mysql import MySqlConnector
from dagr.db.connectors.sqlite import SqliteConnector
from dagr.db.common import SessionManagerException, \
                           BrokerInstantiationException
from sqlalchemy.pool import Pool
from sqlalchemy import exc, event


BASE = declarative_base()


@event.listens_for(Pool, "checkout")
def ping_connection(dbapi_connection, connection_record, connection_proxy):
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")

    except:
        # optional - dispose the whole pool
        # instead of invalidating one at a time
        # connection_proxy._pool.dispose()

        # raise DisconnectionError - pool will try
        # connecting again up to three times before raising.
        Log.getLogger('PingConnection').debug('Connection gone stale')
        raise exc.DisconnectionError()
    cursor.close()


class SessionManager:
  """
  sessionClazz manager for the session handling
  """

  instance = None

  def __init__(self, configFile, createInstance=True):
    # load __config foo!!
    self.__config = Configuration(configFile, 'SessionManager')
    # setup connection string and engine
    protocol = self.__config.get('protocol')

    if (protocol == 'sqlite'):
      self.connector = SqliteConnector(self.__config)
      pass
    elif (protocol == 'mysql') or (protocol == 'mysql+mysqlconnector'):
      self.connector = MySqlConnector(self.__config)
    else:
      raise SessionManagerException(('Protocol {0} '
                                    + 'is undefined').format(protocol))

    if createInstance:
      SessionManager.instance = self

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
    broker = clazz(self.connector.getSession())
    return broker

  @classmethod
  def getInstance(cls):
    """
    Returns the instance (Singleton pattern)

    :returns: WebConfig
    """
    if SessionManager.instance is None:
      raise IndentationError('No SessionManager present')
    return SessionManager.instance

  def close(self):
    self.connector.close()

  def getSession(self):
    return self.connector.getSession()
