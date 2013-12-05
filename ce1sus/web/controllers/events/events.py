# -*- coding: utf-8 -*-

"""
module handing the events pages

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from datetime import datetime
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from ce1sus.web.helpers.protection import require, requireReferer


class EventsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the events page

    :returns: generated HTML
    """
    template = self.getTemplate('/events/eventsBase.html')
    self.setAdminArea(False)
    return template.render()

  @require(requireReferer(('/internal')))
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
    cbAnalysisValues = Analysis.getDefinitions()
    cbRiskValues = Risk.getDefinitions()
    return template.render(event=None,
                           cbStatusValues=cbStatusValues,
                           cbTLPValues=cbTLPValues,
                           cbAnalysisValues=cbAnalysisValues,
                           cbRiskValues=cbRiskValues,
                           today=datetime.now())

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def recent(self):
    """
    Renders the event Page (list of all events)

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/recent.html')

    labels = [{'identifier':'#'},
              {'title':'Title'},
              {'analysis': 'Analysis'},
              {'risk':'Risk'},
              {'status': 'Status'},
              {'tlp':'TLP'},
              {'modified':'Last modification'},
              {'last_seen':'Last seen'}]
    # get only the last 200 events to keep the page small
    user = self.getUser()
    lists = self.eventBroker.getAllForUser(user, 200, 0)
    paginatorOptions = PaginatorOptions('/events/recent',
                                        'eventsTabTabContent')
    paginatorOptions.addOption('NEWTAB',
                               'VIEW',
                               '/events/event/view/',
                               contentid='')
    paginator = Paginator(items=lists,
                          labelsAndProperty=labels,
                          paginatorOptions=paginatorOptions)
    paginator.sortColumn = 'modified'
    paginator.itemsPerPage = 100
    return template.render(paginator=paginator)
