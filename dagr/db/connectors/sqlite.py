

from dagr.db.common import Connector, SessionObject, SessionManagerException, ConnectorException
import cherrypy
from dagr.db.recepie.satool import SATool, SAEnginePlugin
import os
import socket
from sqlalchemy.interfaces import PoolListener
from cherrypy.process import plugins
from sqlalchemy import create_engine, exc, event
from sqlalchemy.orm import scoped_session, sessionmaker
import cherrypy
from sqlalchemy.pool import Pool
from dagr.helpers.debug import Log
from os.path import isfile
from os import getcwd

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
    return self.__session


class SqliteConnector(Connector):

  def __init__(self, config):
      Connector.__init__(self, config)
      dbFile = self.config.get('db')
      if not isfile(dbFile):
        raise ConnectorException('Cannot find file {0} in {1}'.format(dbFile,
                                                                      getcwd()))
      connetionString = 'sqlite:///{db}'.format(db=dbFile)
      self.engine = create_engine(connetionString,
                                  listeners=[ForeignKeysListener()],
                                  echo=self.debug)
      self.sessionClazz = scoped_session(sessionmaker(bind=self.engine,
                                                      autocommit=False,
                                                      autoflush=False))
      self.session = self.sessionClazz()

  def getSession(self):
    return SqliteSession(self.session)

  def getDirectSession(self):
    return self.session

