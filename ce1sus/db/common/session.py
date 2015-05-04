# -*- coding: utf-8 -*-

"""
module for session handling and brokers

Created Jul, 2013
"""
from abc import abstractmethod
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import exc, event
from sqlalchemy.ext.declarative import declarative_base, declared_attr
from sqlalchemy.pool import Pool
from sqlalchemy.schema import Column
from sqlalchemy.types import Unicode, BigInteger
from uuid import UUID
import uuid

from ce1sus.db.common.broker import BrokerBase
from ce1sus.db.common.common import SessionManagerException, BrokerInstantiationException, ORMException
from ce1sus.db.common.connectors.mysql import MySqlConnector
from ce1sus.db.common.connectors.sqlite import SqliteConnector


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class fakefloat(float):
    def __init__(self, value):
        self._value = value

    def __repr__(self):
        return str(self._value)


class BaseClass(object):
  __abstract__ = True

  @declared_attr
  def __tablename__(cls):
      return u'{0}s'.format(cls.__name__.lower())

  @declared_attr
  def identifier(cls):
    return Column(u'{0}_id'.format(cls.__name__.lower()),
                  BigInteger,
                  primary_key=True,
                  autoincrement=True,
                  nullable=False,
                  index=True,
                  unique=True)

  @declared_attr
  def uuid(cls):
    return Column('uuid',
                  Unicode(45, collation='utf8_unicode_ci'),
                  default=uuid.uuid4,
                  nullable=False,
                  index=True,
                  unique=True)

  @abstractmethod
  def validate(self):
    raise ORMException(u'Validate method not implemented for {0}'.format(self.__class__.__name__))

  @staticmethod
  def convert_value(value):
    # TODO: rethink the wrapped file foo
    """converts the value None to '' else it will be send as None-Text"""
    if value or value == 0:
      if isinstance(value, datetime):
        # return value.strftime('%m/%d/%Y %H:%M:%S %Z')
        return value.isoformat()
      if isinstance(value, date):
        # return value.strftime('%Y-%m-%d')
        return value.isoformat()
      if isinstance(value, UUID):
        return u'{0}'.format(value)
      if isinstance(value, Decimal):
        return fakefloat(value)
      return value
    else:
      return ''

Base = declarative_base(cls=BaseClass)


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

  def __init__(self, config, session=None):
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
    self.__direct_session = session
    self.__brokers = dict()

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
      if self.__direct_session:
        session = self.__direct_session
      else:
        session = self.connector.get_session()
    else:
      if not self.__direct_session:
        self.__direct_session = self.connector.get_direct_session()
      session = self.__direct_session

    session_id = id(session)
    session_brokers = self.__brokers.get(session_id, None)
    if session_brokers:
      broker = session_brokers.get(clazz.__name__, None)
      if broker:
        return broker
      else:
        broker = clazz(session)
        self.__brokers[session_id][clazz.__name__] = broker
        return broker
    else:
      self.__brokers[session_id] = dict()
      broker = clazz(session)
      self.__brokers[session_id][clazz.__name__] = broker
      return broker

  def close(self):
    """
    Closes the connections
    """
    self.connector.close()
