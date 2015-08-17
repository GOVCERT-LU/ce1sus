# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 17, 2015
"""
import cherrypy
import os
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.scoping import scoped_session
from sqlalchemy.orm.session import sessionmaker
from sqlalchemy.pool import QueuePool

from ce1sus.db.common.common import SessionObject, Connector
from ce1sus.db.common.recepie.satool import SAEnginePlugin, SATool


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class GenericSession(SessionObject):
  """
  Session wrapper
  """

  def __init__(self, session=None):
    super(SessionObject, self).__init__()
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


class GenericConnector(Connector):
  """
  Connector for mysql dbs
  """
  def __init__(self, config):
    super(GenericConnector, self).__init__(config)
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
        SAEnginePlugin(cherrypy.engine, self).subscribe()
        self.sa_tool = SATool(self)
        cherrypy.tools.db = self.sa_tool
        cherrypy.config.update({'tools.db.on': 'True'})
      self.session = None
    else:
      self.session = self.get_direct_session()

  def get_engine(self):
    """
    Returns the engine
    """
    if self.engine:
      return self.engine
    else:
      return self.create_engine()

  def get_direct_session(self, instanciated=True):
    """
    Returns the session from the engine
    """
    self.engine = self.get_engine()
    session = scoped_session(sessionmaker(bind=self.engine,
                                          autocommit=False,
                                          autoflush=False))
    if instanciated:
      session = session()
    return GenericSession(session)

  def get_session(self):
    """
    Returns the session

    :returns: SqliteSession
    """
    return GenericSession(self.session)

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
    return create_engine(self.connection_string,
                         poolclass=QueuePool,
                         echo=self.debug,
                         encoding='utf-8',
                         pool_recycle=3600,
                         pool_size=10,
                         max_overflow=10)
