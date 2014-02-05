"""main file for launching ce1sus"""

import os
import cherrypy
from dagr.db.session import SessionManager
from dagr.helpers.debug import Log
from dagr.web.helpers.templates import MakoHandler
from dagr.web.helpers.webexceptions import ErrorHandler
from ce1sus.common.system import System
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
from ce1sus.web.views.admin.index import AdminView
from ce1sus.web.views.admin.attributes import AdminAttributeView
# from ce1sus.web.views.admin.groups import AdminGroupView
from ce1sus.web.views.admin.objects import AdminObjectsView
# from ce1sus.web.views.admin.subgroups import AdminSubGroupView
# from ce1sus.web.views.admin.user import AdminUserView
from ce1sus.web.views.admin.validation import AdminValidationView

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
  load_rest_api = config.get('ce1sus', 'enablerestapi', default_value=False)

  # Setup logger
  logger = Log(config)
  logger.get_logger('BootStrap').debug("Loading System...")

  system = System(config)
  logger.get_logger('BootStrap').debug("Performing System checks...")
  system.perform_web_checks()
  if load_rest_api:
    logger.get_logger('BootStrap').debug("Performing REST API checks...")
    system.perform_rest_api_startup_checks()
  system.close()

  logger.get_logger('BootStrap').debug("Loading ErrorHandler...")
  ErrorHandler(config)



  logger.get_logger('BootStrap').debug("Loading Views...")
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
  cherrypy.tree.mount(AdminView(config), '/admin')
  # cherrypy.tree.mount(AdminUserView(config), '/admin/users')
  # cherrypy.tree.mount(AdminGroupView(config), '/admin/groups')
  cherrypy.tree.mount(AdminObjectsView(config), '/admin/objects')
  cherrypy.tree.mount(AdminAttributeView(config), '/admin/attributes')
  # cherrypy.tree.mount(AdminSubGroupView(config), '/admin/subgroups')
  cherrypy.tree.mount(AdminValidationView(config), '/admin/validation')

  if load_rest_api:
    logger.get_logger('BootStrap').debug("Loading Rest...")
    # cherrypy.tree.mount(RestController(ce1susConfigFile), '/REST/')
  else:
    logger.get_logger('BootStrap').debug("Loading Rest skipped. Disabled in config")

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
