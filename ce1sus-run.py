"""main file for launching ce1sus"""

import cherrypy
import os
from framework.db.session import SessionManager
from framework.helpers.debug import Log
from framework.web.helpers.templates import MakoHandler
from ce1sus.web.controllers.index import IndexController
from ce1sus.web.controllers.admin.index import AdminController
from ce1sus.web.controllers.events.events import EventsController
from ce1sus.web.controllers.admin.user import UserController
from ce1sus.web.controllers.admin.groups import GroupController
from ce1sus.web.controllers.admin.objects import ObjectController
from ce1sus.web.helpers.protection import Protector
from framework.web.helpers.webexceptions import ErrorHandler
from framework.helpers.ldaphandling import LDAPHandler
from framework.helpers.rt import RTHelper
from framework.web.helpers.config import WebConfig
from framework.web.helpers.cherrypyhandling import CherryPyHandler
from ce1sus.web.controllers.admin.attributes import AttributeController
from ce1sus.web.controllers.event.event import EventController
from ce1sus.web.controllers.event.objects import ObjectsController
from ce1sus.web.controllers.event.tickets import TicketsController
from ce1sus.web.controllers.event.groups import GroupsController
from ce1sus.web.controllers.events.search import SearchController
from ce1sus.web.controllers.event.attributes import AttributesController
from ce1sus.web.controllers.event.comments import CommentsController

def application(environ, start_response):
  bootstrap()
  return CherryPyHandler.application(environ, start_response)



def bootstrap():
  # want parent of parent directory aka ../../
  basePath = os.path.dirname(os.path.abspath(__file__))

  # setup cherrypy
  CherryPyHandler(basePath + '/config/cherrypy.conf')

  ce1susConfigFile = basePath + '/config/ce1sus.conf'

  # Load 'Modules'
  SessionManager(ce1susConfigFile)
  # ErrorHandler(ce1susConfigFile)
  Log(ce1susConfigFile)
  MakoHandler(ce1susConfigFile)
  Protector(ce1susConfigFile)
  RTHelper(ce1susConfigFile)
  WebConfig(ce1susConfigFile)
  LDAPHandler(ce1susConfigFile)


  # add controllers
  CherryPyHandler.addController(IndexController(), '/')
  CherryPyHandler.addController(AdminController(), '/admin')
  CherryPyHandler.addController(UserController(), '/admin/users')
  CherryPyHandler.addController(GroupController(), '/admin/groups')
  CherryPyHandler.addController(ObjectController(), '/admin/objects')
  CherryPyHandler.addController(AttributeController(), '/admin/attributes')
  CherryPyHandler.addController(EventsController(), '/events')
  CherryPyHandler.addController(EventController(), '/events/event')
  CherryPyHandler.addController(SearchController(), '/events/search')
  CherryPyHandler.addController(ObjectsController(), '/events/event/objects')
  CherryPyHandler.addController(TicketsController(), '/events/event/tickets')
  CherryPyHandler.addController(GroupsController(), '/events/event/groups')
  CherryPyHandler.addController(AttributesController(), '/events/event/attribute')
  CherryPyHandler.addController(CommentsController(), '/events/event/comment')




if __name__ == '__main__':

  bootstrap()
  CherryPyHandler.localRun()

