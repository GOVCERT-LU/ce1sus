# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.common import Connector, SessionObject, SessionManagerException
from dagr.db.recepie.satool import SATool, SAEnginePlugin
import os
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from dagr.helpers.debug import Log
import cherrypy


class MySqlSession(SessionObject):

  def __init__(self, session=None):
    SessionObject.__init__(self)
    self.__session = session

  def getSession(self):
    if self.__session:
      return self.__session
    else:
      return cherrypy.request.db


class MySqlConnector(Connector):

  def __init__(self, config):
    Connector.__init__(self, config)
    hostname = self.config.get('host')
    port = self.config.get('port')
    # check if host is available
    response = os.system("ping -c 1 " + hostname)
    if response != 0:
      raise SessionManagerException('Host "{hostname}" not ' +
                                     'available'.format(hostname=hostname))
    # check if socket available
    if not MySqlConnector.isServiceExisting(hostname, port):
      raise SessionManagerException('Service on "{hostname}:{port}"' +
                                    ' not available'.format(hostname=hostname,
                                                            port=port))
    self.connectionString = ('{prot}://{user}:{password}@'
                             + '{host}:{port}/{db}').format(
                                          prot=self.protocol,
                                          user=self.config.get('username'),
                                          password=self.config.get('password'),
                                          host=hostname,
                                          db=self.config.get('db'),
                                          port=port
                                        )
    if self.config.get('usecherrypy'):
      SAEnginePlugin(cherrypy.engine,
                     self.connectionString,
                     self.debug).subscribe()
      self.saTool = SATool()
      cherrypy.tools.db = self.saTool
      self.session = None
      cherrypy.config.update({'tools.db.on': 'True'})
    else:
      self.session = self.getDirectSession()

  def getDirectSession(self):
    self.engine = create_engine(self.connectionString,
                                  echo=self.debug,
                                  echo_pool=self.debug)
    self.sessionClazz = scoped_session(sessionmaker(bind=self.engine,
                                                      autocommit=False,
                                                      autoflush=False))
    return self.sessionClazz()

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

  def getSession(self):
    return MySqlSession(self.session)

  def close(self):
    self.session = None
    self.engine.dispose()
    self.engine = None

  def createEngine(self):
    return create_engine(self.connectionString,
                                  echo=self.debug,
                                  echo_pool=self.debug)
