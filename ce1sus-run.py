"""main file for launching ce1sus"""

import cherrypy
import os
from ce1sus.db.session import SessionManager
from ce1sus.helpers.debug import Log
from ce1sus.web.helpers.templates import MakoHandler
from ce1sus.web.controllers.index import IndexController
from ce1sus.web.controllers.admin import AdminController
from ce1sus.web.controllers.event import EventController
from ce1sus.web.helpers.protection import Protector
from ce1sus.helpers.ldaphandling import LDAPHandler
from ce1sus.helpers.rt import RTHelper
from ce1sus.web.helpers.config import WebConfig



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
  basePath = os.path.dirname(os.path.abspath(__file__))

  loadCerryPyConfig(basePath + '/config/cherrypy.conf')

  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  SessionManager(ce1susConfigFile)
  # ErrorHandler(ce1susConfigFile)
  Log(ce1susConfigFile)
  MakoHandler(ce1susConfigFile)
  Protector(ce1susConfigFile)
  RTHelper(ce1susConfigFile)
  WebConfig(ce1susConfigFile)
  LDAPHandler(ce1susConfigFile)

  config = {'/':
                  {
                   'tools.staticdir.on': True,
                   'tools.staticdir.root': basePath + "/htdocs",
                   'tools.staticdir.dir': "",
                   'tools.sessions.on': True,
                   'tools.sessions.storage_type': 'file',
                   'tools.sessions.storage_path' : basePath + '/sessions',
                   'tools.sessions.timeout': 60,
                   'tools.auth.on': True

                  }
            }
  cherrypy.tree.mount(IndexController(), '/', config=config)
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

