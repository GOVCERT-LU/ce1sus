"""main file for launching ce1sus"""

import os
import cherrypy
from dagr.db.session import SessionManager
from dagr.helpers.debug import Log
from dagr.web.helpers.templates import MakoHandler
from dagr.web.helpers.webexceptions import ErrorHandler
from ce1sus.common.system import System

from dagr.helpers.ldaphandling import LDAPHandler
from dagr.helpers.rt import RTTickets
# from ce1sus.sanity import SantityChecker
from dagr.helpers.mailer import Mailer



from ce1sus.web.views.index import IndexView
from ce1sus.web.views.events.events import EventsView
from ce1sus.web.views.event.event import EventView
from ce1sus.web.views.events.search import SearchView
from ce1sus.web.views.event.objects import ObjectsView
from ce1sus.web.views.event.comments import CommentsView
from ce1sus.web.views.common.bitvalue import BitValueView
from ce1sus.web.views.event.attributes import AttributesView
from ce1sus.web.views.event.groups import GroupsView


from dagr.helpers.config import Configuration
from ce1sus.web.views.common.decorators import require, check_auth

from ce1sus.brokers.system.ce1susbroker import Ce1susBroker

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
  except cherrypy._cperror as error:
    raise ConfigException(error)

  # instantiate auth module
  cherrypy.tools.auth = cherrypy.Tool('before_handler', check_auth)

  # load config file
  config = Configuration(ce1susConfigFile)

  # Setup logger
  logger = Log(config)
  logger.get_logger("run").debug("Loading System...")

  system = System(config)
  system.perform_web_checks()

  logger.get_logger("run").debug("Loading ErrorHandler...")
  ErrorHandler(config)



  logger.get_logger("run").debug("Loading Views...")
  # Load 'Modules'
  cherrypy.tree.mount(IndexView(config), '/')
  cherrypy.tree.mount(EventsView(config), '/events')
  cherrypy.tree.mount(SearchView(config), '/events/search')
  cherrypy.tree.mount(EventView(config), '/events/event')
  cherrypy.tree.mount(ObjectsView(config), '/events/event/objects')
  cherrypy.tree.mount(CommentsView(config), '/events/event/comment')
  cherrypy.tree.mount(BitValueView(config), '/events/event/bit_value')
  cherrypy.tree.mount(AttributesView(config), '/events/event/attribute')
  cherrypy.tree.mount(GroupsView(config), '/events/event/groups')

  """
  Mailer(ce1susConfigFile)


  Log.getLogger("run").debug("Loading Configuration file")
  config =

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
  cherrypy.tree.mount(BitValueController(), '/events/event/bitValue')
  # RESTFoo
  cherrypy.tree.mount(RestController(ce1susConfigFile), '/REST/')
  """

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
