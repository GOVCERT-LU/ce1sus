"""module holding all controllers needed for the event handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.web.controllers.base import BaseController
import cherrypy
from framework.web.helpers.pagination import Paginator, PaginatorOptions
from datetime import datetime
from ce1sus.brokers.eventbroker import EventBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel
from ce1sus.web.helpers.protection import require
from ce1sus.web.helpers.protection import privileged
class EventsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)


  @require(privileged())
  @cherrypy.expose
  def index(self):

    """
    renders the events page

    :returns: generated HTML
    """
    template = self.getTemplate('/events/eventsBase.html')
    return template.render()


  @require()
  @cherrypy.expose
  def addEvent(self):
    """
    Renders the page for adding an event

    :param event: Is not null in case of an erroneous input
    :type event: Event

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/addEvent.html')

    cbStatusValues = Status.getDefinitions()
    cbTLPValues = TLPLevel.getDefinitions()

    return template.render(event=None,
                           cbStatusValues=cbStatusValues,
                           cbTLPValues=cbTLPValues,
                           today=datetime.now())


  @require()
  @cherrypy.expose
  def recent(self):
    """
    Renders the event Page (list of all events)

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/recent.html')

    labels = [{'identifier':'#'},
              {'label':'Title'},
              {'modified':'Last modification'},
              {'last_seen':'Last seen'},
              {'status': 'Status'},
              {'tlp':'TLP'}]

    # get only the last 200 events to keep the page small
    user = self.getUser()
    lists = self.eventBroker.getAllForUser(user, 200, 0)


    paginatorOptions = PaginatorOptions('/events/recent', 'eventsTabTabContent')
    paginatorOptions.addOption('NEWTAB',
                               'VIEW',
                               '/events/event/view/',
                               contentid='')
    paginator = Paginator(items=lists,
                          labelsAndProperty=labels,
                          paginatorOptions=paginatorOptions)
    paginator.itemsPerPage = 100

    return template.render(paginator=paginator)

