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
    """
    Keep alive check
    """
    del connection_proxy, connection_record
    cursor = dbapi_connection.cursor()
    try:
        cursor.execute("SELECT 1")
    except:
        raise exc.DisconnectionError()
    cursor.close()


class SessionManager:
  """
  sessionClazz manager for the session handling
  """

  def __init__(self, config):
    """
    Creator

    :param config: The configuration for this module
    :type config: Configuration

    :returns: SessionManager
    """
    # load __config foo!!
    self.__config_section = config.get_section('SessionManager')
    # setup connection string and engine
    protocol = self.__config_section.get('protocol')

    if (protocol == 'sqlite'):
      self.connector = SqliteConnector(self.__config_section)
    elif ('mysql' in protocol):
      self.connector = MySqlConnector(self.__config_section)
    else:
      raise SessionManagerException(('Protocol {0} '
                                    + 'is undefined').format(protocol))
    self.__direct_session = None

  def broker_factory(self, clazz):
    """
    Creates and initializes a broker

    :param clazz: broker class
    :type clazz: extension of BrokerBase

    :returns: instance of a Broker
    """
    if not issubclass(clazz, BrokerBase):
      raise BrokerInstantiationException('Class does not ' +
                                         'implement BrokerBase')
    if self.__config_section.get('usecherrypy', False):
      session = self.connector.get_session()
    else:
      if not self.__direct_session:
        self.__direct_session = self.connector.get_direct_session()
      session = self.__direct_session
    broker = clazz(session)
    return broker

  def close(self):
    """
    Closes the connections
    """
    self.connector.close()
