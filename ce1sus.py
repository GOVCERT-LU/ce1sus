

import cherrypy
import os
from ce1sus.db.session import SessionManager
from ce1sus.helpers.debug import Logger
from ce1sus.web.helpers.templates import MakoHandler
from ce1sus.web.controllers.index import IndexController
from ce1sus.web.controllers.admin import AdminController
from ce1sus.web.helpers.webexceptions import ErrorHandler
from ce1sus.web.controllers.event import EventController


class InstantiationException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

class ConfigException(Exception):

  def __init__(self, message):
    Exception.__init__(self, message)

def loadCerryPyConfig(configFile):

  def parseAndSet(line):
    splitedLine = line.split('=')
    if len(splitedLine) == 2:
      key = splitedLine[0].strip()
      value = splitedLine[1].strip()

      # Keeping booleanValues
      if (value.upper() in ['YES', 'TRUE']):
        value = True
      else:
        if (value.upper() in [ 'NO', 'FALSE']):
          value = False

      cherrypy.config[key] = value

    else:
      raise InstantiationException('Error in config for line :' + line);

  # check if file exists
  if os.path.isfile(configFile):
    # read lines
    for line in open(configFile, 'r'):
      parseAndSet(line)

  else:
    raise ConfigException('Could not find config file ' + configFile)

def application(environ, start_response):
  bootstap()
  return cherrypy.tree(environ, start_response)



def bootstap():
  # want parent of parent directory aka ../../
  basePath = os.path.abspath(os.getcwd())
  # s

  loadCerryPyConfig(basePath + '/config/cherrypy.conf')



  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  SessionManager(ce1susConfigFile)
  # ErrorHandler(ce1susConfigFile)
  Logger(ce1susConfigFile)
  MakoHandler(ce1susConfigFile)
  config = {'/':
                  {
                   'tools.staticdir.on': True,
                   'tools.staticdir.root': os.path.join(os.path.abspath("."), u"htdocs"),
                   'tools.staticdir.dir': "",

                  }
            }
  cherrypy.tree.mount(IndexController(), '/', config=config)
  cherrypy.tree.mount(IndexController(), '/index', config=config)
  cherrypy.tree.mount(AdminController(), '/admin', config=config)
  cherrypy.tree.mount(EventController(), '/events', config=config)


if __name__ == '__main__':

  bootstap()
  try:
      # this is the way it should be done in cherrypy 3.X
      cherrypy.engine.start()
      cherrypy.engine.block()
  except Exception as e:
    print e

