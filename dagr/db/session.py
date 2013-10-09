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
import os
import socket
from dagr.helpers.debug import Log
from sqlalchemy.ext.declarative import declarative_base
import cherrypy
from dagr.db.recepie.satool import SATool, SAEnginePlugin

BASE = declarative_base()


class SessionManagerException(Exception):
  """sessionClazz Manager Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)


class BrokerInstantiationException(Exception):
  """Broker Instantiation Exception"""
  def __init__(self, message):
    Exception.__init__(self, message)


# pylint: disable=R0903
class SessionObject(object):
  """
  Session container
  """

  # pylint: disable=R0201
  @property
  def session(self):
    """
    returns the session object
    """
    return cherrypy.request.db


class SessionManager:
  """
  sessionClazz manager for the session handling
  """

  def __init__(self, configFile):
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
      SAEnginePlugin(cherrypy.engine, connetionString,
                     False, debug).subscribe()
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

  @staticmethod
  def brokerFactory(clazz):
    """
    Creates and initializes a broker

    :param clazz: broker class
    :type clazz: extension of BrokerBase

    :returns: instance of a Broker
    """
    if not issubclass(clazz, BrokerBase):
      raise BrokerInstantiationException('Class does not ' +
                                         'implement BrokerBase')
    broker = clazz(SessionObject())
    return broker

  def close(self):
    """
    Closes the session
    """
    pass

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Log.getLogger(self.__class__.__name__)
