# -*- coding: utf-8 -*-

"""
Modified version of the SATool

Created 12 Sept 2013
"""


from cherrypy.process import plugins
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import cherrypy


class SAEnginePlugin(plugins.SimplePlugin):
  """The SAEnglinge
  Original found under
  http://www.defuze.org/archives/222-integrating-
                                    sqlalchemy-into-a-cherrypy-application.html
  """

  def __init__(self, bus, connector):
    """
    The plugin is registered to the CherryPy engine and therefore
    is part of the bus (the engine *is* a bus) registery.

    We use this plugin to create the SA engine. At the same time,
    when the plugin starts we create the tables into the database
    using the mapped class of the global metadata.

    Finally we create a new 'bind' channel that the SA tool
    will use to map a session to the SA engine at request time.
    """
    plugins.SimplePlugin.__init__(self, bus)
    self.sa_engine = None
    self.bus.subscribe("bind", self.bind)
    self.connector = connector

  def start(self):
    """Start the engine"""
    self.sa_engine = self.connector.get_engine()

  def stop(self):
    """stops the engine"""
    if self.sa_engine:
      self.sa_engine.dispose()
      self.sa_engine = None

  def bind(self, session):
    """binds the engine"""
    session.configure(bind=self.sa_engine)


class SATool(cherrypy.Tool):
  """The SATool
  Original found under
  http://www.defuze.org/archives/222-integrating-
                                    sqlalchemy-into-a-cherrypy-application.html
  """
  def __init__(self):
    """
    The SA tool is responsible for associating a SA session
    to the SA engine and attaching it to the current request.
    Since we are running in a multithreaded application,
    we use the scoped_session that will create a session
    on a per thread basis so that you don't worry about
    concurrency on the session object itself.

    This tools binds a session to the engine each time
    a requests starts and commits/rollbacks whenever
    the request terminates.
    """
    cherrypy.Tool.__init__(self, 'on_start_resource',
                           self.bind_session,
                           priority=20)

    self.session = scoped_session(sessionmaker(autoflush=False,
                                               autocommit=False))

  def _setup(self):
    cherrypy.Tool._setup(self)
    cherrypy.request.hooks.attach('on_end_resource',
                                  self.commit_transaction,
                                  priority=80)

  def bind_session(self):
    """Binds the session"""
    cherrypy.engine.publish('bind', self.session)
    cherrypy.request.db = self.session

  def commit_transaction(self):
    """Commit transaction"""
    cherrypy.request.db = None
    try:
      #Disabled as I do it my self!!!
      # function = getattr(self.session, 'commit')
      # function()
      pass
    except:
      function = getattr(self.session, 'rollback')
      function()
      raise
    finally:
      self.session.remove()
