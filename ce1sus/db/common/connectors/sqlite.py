# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Aug, 2013
"""
import cherrypy
from os.path import isfile
from sqlalchemy import create_engine
from sqlalchemy.interfaces import PoolListener
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.scoping import scoped_session

from ce1sus.db.common.common import SessionObject, Connector
from ce1sus.db.common.recepie.satool import SAEnginePlugin, SATool


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


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


# pylint: disable=R0903
class SqliteSession(SessionObject):
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


class SqliteConnector(Connector):
  """
  Connector for sqlite dbs
  """
  def __init__(self, config):
    super(Connector, self).__init__(config)
    db_file = self.config.get('db')
    self.engine = None
    if not isfile(db_file):
      # create one
      f = open(db_file, 'w+')
      f.close()
      """
      raise ConnectorException('Cannot find file {0} in {1}'.format(db_file,
                                                                    getcwd()
                                                                    )
                               )
      """
    self.connetion_string = 'sqlite:///{db}'.format(db=db_file)

    if self.config.get('usecherrypy'):
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

  def get_session(self):
    """
    Returns the session

    :returns: SqliteSession
    """
    return SqliteSession(self.session)

  def get_engine(self):
    """
    Returns the engine
    """
    return create_engine(self.connetion_string,
                         listeners=[ForeignKeysListener()],
                         echo=self.debug,
                         echo_pool=self.debug,
                         strategy='plain')

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
    return SqliteSession(session)

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
    Returns a new engine
    """
    return create_engine(self.connetion_string,
                         listeners=[ForeignKeysListener()],
                         echo=self.debug,
                         echo_pool=self.debug,
                         strategy='plain')
