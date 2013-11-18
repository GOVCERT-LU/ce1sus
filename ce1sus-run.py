"""main file for launching ce1sus"""

import os
import cherrypy
from dagr.db.session import SessionManager
from dagr.helpers.debug import Log
from dagr.web.helpers.templates import MakoHandler
from ce1sus.web.controllers.index import IndexController
from ce1sus.web.controllers.admin.index import AdminController
from ce1sus.web.controllers.events.events import EventsController
from ce1sus.web.controllers.admin.user import UserController
from ce1sus.web.controllers.admin.groups import GroupController
from ce1sus.web.controllers.admin.objects import ObjectController
from ce1sus.web.helpers.protection import Protector
from dagr.web.helpers.webexceptions import ErrorHandler
from dagr.helpers.ldaphandling import LDAPHandler
from dagr.helpers.rt import RTTickets
from dagr.web.helpers.config import WebConfig
from ce1sus.web.controllers.admin.attributes import AttributeController
from ce1sus.web.controllers.event.event import EventController
from ce1sus.web.controllers.event.objects import ObjectsController

from ce1sus.web.controllers.event.groups import GroupsController
from ce1sus.web.controllers.events.search import SearchController
from ce1sus.web.controllers.event.attributes import AttributesController
from ce1sus.web.controllers.event.comments import CommentsController
from ce1sus.sanity import SantityChecker
from ce1sus.rest.restcontroller import RestController
from ce1sus.web.controllers.admin.subgroups import SubGroupController
from ce1sus.web.controllers.admin.validation import ValidationController

def bootstrap():
  # want parent of parent directory aka ../../
  basePath = os.path.dirname(os.path.abspath(__file__))

  # setup cherrypy
  #
  # CherryPyHandler(basePath + '/config/cherrypy.conf')

  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  cherrypyConfigFile = basePath + '/config/cherrypy.conf'

  try:
    if os.path.isfile(cherrypyConfigFile):
      cherrypy.config.update(cherrypyConfigFile)
    else:
      raise ConfigException('Could not find config file ' + cherrypyConfigFile)
  except cherrypy._cperror as e:
    raise ConfigException(e)

  sanityChecker = SantityChecker(ce1susConfigFile)
  sanityChecker.checkDB()
  sanityChecker.checkApplication()
  sanityChecker.close()
  sanityChecker = None

  # Load 'Modules'

  ErrorHandler(ce1susConfigFile)
  Log(ce1susConfigFile)
  Log.getLogger("run").debug("Loading Session")
  SessionManager(ce1susConfigFile)


  Log.getLogger("run").debug("Loading Mako")
  MakoHandler(ce1susConfigFile)
  Log.getLogger("run").debug("Loading Protector")
  Protector(ce1susConfigFile)
  Log.getLogger("run").debug("Loading RT")
  RTTickets(ce1susConfigFile)
  Log.getLogger("run").debug("Loading WebCfg")
  WebConfig(ce1susConfigFile, 'ce1sus')
  Log.getLogger("run").debug("Loading Ldap")
  LDAPHandler(ce1susConfigFile)

  # add controllers
  Log.getLogger("run").debug("Adding controllers")
  Log.getLogger("run").debug("Adding index")
  cherrypy.tree.mount(IndexController(), '/')
  Log.getLogger("run").debug("Adding admin")
  cherrypy.tree.mount(AdminController(), '/admin')
  Log.getLogger("run").debug("Adding admin/users")
  cherrypy.tree.mount(UserController(), '/admin/users')
  Log.getLogger("run").debug("Adding admin groups")
  cherrypy.tree.mount(GroupController(), '/admin/groups')
  Log.getLogger("run").debug("Adding admin objects")
  cherrypy.tree.mount(ObjectController(), '/admin/objects')
  Log.getLogger("run").debug("Adding admin attributes")
  cherrypy.tree.mount(AttributeController(), '/admin/attributes')
  Log.getLogger("run").debug("Adding events")
  cherrypy.tree.mount(EventsController(), '/events')
  Log.getLogger("run").debug("Adding events event")
  cherrypy.tree.mount(EventController(), '/events/event')
  Log.getLogger("run").debug("Adding events search")
  cherrypy.tree.mount(SearchController(), '/events/search')
  Log.getLogger("run").debug("Adding events event object")
  cherrypy.tree.mount(ObjectsController(), '/events/event/objects')
  Log.getLogger("run").debug("Adding events event groups")
  cherrypy.tree.mount(GroupsController(), '/events/event/groups')
  Log.getLogger("run").debug("Adding events event attribute")
  cherrypy.tree.mount(AttributesController(), '/events/event/attribute')
  Log.getLogger("run").debug("Adding events event comment")
  cherrypy.tree.mount(CommentsController(), '/events/event/comment')
  cherrypy.tree.mount(SubGroupController(), '/admin/subgroups')
  cherrypy.tree.mount(ValidationController(), '/admin/validation')

  # RESTFoo
  cherrypy.tree.mount(RestController(ce1susConfigFile), '/REST/')
if __name__ == '__main__':

  bootstrap()
  try:
    cherrypy.engine.start()
    cherrypy.engine.block()
  except cherrypy._cperror as e:
    raise ConfigException(e)
else:
  bootstrap()
  cherrypy.engine.start()
  application = cherrypy.tree
