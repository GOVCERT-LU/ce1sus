# -*- coding: utf-8 -*-

"""
module for session handling and brokers

Created Jul, 2013
"""
from abc import abstractmethod
from ce1sus_api.api.restclasses import Ce1susWrappedFile
from sqlalchemy import exc, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import declared_attr
from sqlalchemy.pool import Pool
from sqlalchemy.schema import Column
from sqlalchemy.types import BIGINT, Unicode
import uuid
from datetime import datetime

from ce1sus.db.common.broker import BrokerBase
from ce1sus.db.common.common import SessionManagerException, BrokerInstantiationException, ORMException
from ce1sus.db.common.connectors.mysql import MySqlConnector
from ce1sus.db.common.connectors.sqlite import SqliteConnector


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Base(object):
  __abstract__ = True

  @declared_attr
  def __tablename__(cls):
      return u'{0}s'.format(cls.__name__.lower())

  @declared_attr
  def identifier(cls):
    return Column(u'{0}_id'.format(cls.__name__.lower()), BIGINT, primary_key=True, nullable=False, index=True)

  @declared_attr
  def uuid(cls):
    return Column('uuid', Unicode(45), default=uuid.uuid4(), nullable=False, index=True)

  @abstractmethod
  def validate(self):
    raise ORMException(u'Validate method not implemented for {0}'.format(self.__class__.__name__))

  @staticmethod
  def convert_value(value):
    # TODO: rethink the wrapped file foo
    """converts the value None to '' else it will be send as None-Text"""
    if value or value == 0:
      if isinstance(value, Ce1susWrappedFile):
        return value.get_api_wrapped_value()
      if isinstance(value, datetime):
        return value.strftime('%m/%d/%Y %H:%M:%S %Z')
      return value
    else:
      return ''

Base = declarative_base(cls=Base)


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
