# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Aug, 2013
"""
import cherrypy
import os
import socket
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from ce1sus.db.common.common import SessionObject, SessionManagerException, Connector
from ce1sus.db.common.recepie.satool import SAEnginePlugin, SATool


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MySqlSession(SessionObject):
  """
  Session wrapper
  """

  def __init__(self, session=None):
    SessionObject.__init__(self)
    self.__session = session

  def get_session(self):
    """
    Returns a session
    """
    if self.__session:
      return self.__session
    else:
      return cherrypy.request.db

  def close(self):
    if self.__session:
      self.__session.close()


class MySqlConnector(Connector):
  """
  Connector for mysql dbs
  """
  def __init__(self, config):
    Connector.__init__(self, config)
    hostname = self.config.get('host')
    port = self.config.get('port')
    self.engine = None
    self.connection_string = ('{prot}://{user}:{password}@{host}:{port}/{db}').format(prot=self.protocol,
                                                                                      user=self.config.get('username'),
                                                                                      password=self.config.get('password'),
                                                                                      host=hostname,
                                                                                      db=self.config.get('db'),
                                                                                      port=port
                                                                                      )
    if self.config.get('usecherrypy'):
      # check if not already instantiated
      try:
        getattr(cherrypy.tools, 'db')
      except AttributeError:
        self.__check_if_existing(hostname, port)
        SAEnginePlugin(cherrypy.engine, self).subscribe()
        self.sa_tool = SATool()
        cherrypy.tools.db = self.sa_tool
        cherrypy.config.update({'tools.db.on': 'True'})
      self.session = None
    else:
      self.__check_if_existing(hostname, port)
      self.session = self.get_direct_session()

  def __check_if_existing(self, hostname, port):
    # check if host is available
    response = os.system("ping -c 1 " + hostname)
    if response != 0:
      raise SessionManagerException('Host "{hostname}" not available'.format(hostname=hostname))
    # check if socket available
    if not self.is_service_existing(hostname, port):
      raise SessionManagerException('Service on "{hostname}:{port}" not available'.format(hostname=hostname,
                                                                                          port=port))

  def get_engine(self):
    """
    Returns the engine
    """
    if self.engine:
      return self.engine
    else:
      return create_engine(self.connection_string + '?charset=utf8',
                           echo=self.debug,
                           echo_pool=self.debug,
                           encoding='utf-8')

  def get_direct_session(self):
    """
    Returns the session from the engine
    """
    self.engine = self.get_engine()
    session = scoped_session(sessionmaker(bind=self.engine,
                                          autocommit=False,
                                          autoflush=False))()
    return MySqlSession(session)

  def is_service_existing(self, host, port):
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
      socket_obj = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      socket_obj.settimeout(1)
      socket_obj.connect((host, port))
      socket_obj.close()
    except socket.error:
      return False
    return True

  def get_session(self):
    """
    Returns the session

    :returns: SqliteSession
    """
    return MySqlSession(self.session)

  def close(self):
    """
    Closes the session
    """
    self.session = None
    if self.engine:
      self.engine.dispose()
      self.engine = None

  def create_engine(self):
    """
    Returns the engine
    """
    return create_engine(self.connection_string + '?charset=utf8',
                         echo=self.debug,
                         echo_pool=self.debug,
                         encoding='utf-8',
                         pool_recycle=3600,
                         pool_size=10)
