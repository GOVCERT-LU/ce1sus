
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import os
import cherrypy
from framework.helpers.debug import Log


class CherryPyException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

class ConfigException(CherryPyException):

  def __init__(self, message):
    CherryPyException.__init__(self, message)


class CherryPyHandler(object):

  def __init__(self, configFile):
      # check if file exists
    #Log.getLogger(self.__class__.__name__).debug("init Handler")
    try:
      if os.path.isfile(configFile):
        cherrypy.config.update(configFile)
      else:
        raise ConfigException('Could not find config file ' + configFile)
    except cherrypy._cperror as e:
      raise ConfigException(e)

  @staticmethod
  def addController(clazz, urlPath):
    # check if the class variable is an instance or not
    if isinstance(clazz, type):
      cherrypy.tree.mount(clazz(), urlPath)
    else:
      cherrypy.tree.mount(clazz, urlPath)

  @staticmethod
  def application(environ, start_response):
    #Log.getLogger(self.__class__.__name__).debug("Run application method")
    cherrypy.tree(environ, start_response)

  @staticmethod
  def localRun():
    try:
      # this is the way it should be done in cherrypy 3.X
      cherrypy.engine.start()
      cherrypy.engine.block()
    except cherrypy._cperror as e:
      raise ConfigException(e)
