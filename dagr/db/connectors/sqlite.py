# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.common import Connector, SessionObject, ConnectorException
from sqlalchemy.interfaces import PoolListener
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os.path import isfile
from os import getcwd
from dagr.db.recepie.satool import SATool, SAEnginePlugin
import cherrypy


class ForeignKeysListener(PoolListener):
  """
  Foreign Key listener to set the foreign_keys
  """
  # pylint: disable=W0613
  def connect(self, dbapi_connection, connection_record):
    """
    overridden method of PoolListener
    """
    db_cursor = dbapi_connection.execute('pragma foreign_keys=ON')
    db_cursor.close()


class SqliteSession(SessionObject):

  def __init__(self, session=None):
    SessionObject.__init__(self)
    self.__session = session

  def getSession(self):
    if self.__session:
      return self.__session
    else:
      return cherrypy.request.db


class SqliteConnector(Connector):

  def __init__(self, config):
    Connector.__init__(self, config)
    dbFile = self.config.get('db')
    if not isfile(dbFile):
      raise ConnectorException('Cannot find file {0} in {1}'.format(dbFile,
                                                                    getcwd()
                                                                    )
                               )
    self.connetionString = 'sqlite:///{db}'.format(db=dbFile)

    if self.config.get('usecherrypy'):
      SAEnginePlugin(cherrypy.engine,
                     self.connetionString,
                     self.debug).subscribe()
      self.saTool = SATool()
      cherrypy.tools.db = self.saTool
      self.session = None
      cherrypy.config.update({'tools.db.on': 'True'})
    else:
      self.session = self.getDirectSession()

  def getSession(self):
    return SqliteSession(self.session)

  def getDirectSession(self):
    self.engine = create_engine(self.connetionString,
                                  listeners=[ForeignKeysListener()],
                                  echo=self.debug,
                                  echo_pool=self.debug,
                                  strategy='plain')
    self.sessionClazz = sessionmaker(bind=self.engine,
                                     autocommit=False,
                                     autoflush=False)
    return self.sessionClazz()

  def close(self):
    self.session = None
    self.engine.dispose()
    self.engine = None

  def createEngine(self):
        return create_engine(self.connetionString,
                                  listeners=[ForeignKeysListener()],
                                  echo=self.debug,
                                  echo_pool=self.debug,
                                  strategy='plain')
