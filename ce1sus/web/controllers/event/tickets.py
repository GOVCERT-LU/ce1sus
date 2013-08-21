"""module holding all controllers needed for the event handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import copy
from framework.web.controllers.base import BaseController
import cherrypy
from framework.web.helpers.pagination import Paginator, PaginatorOptions
from datetime import datetime
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, \
                  AttributeBroker, Event, Object, Attribute, Comment, \
                  CommentBroker, Ticket, TicketBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel
from ce1sus.brokers.definitionbroker import ObjectDefinitionBroker, \
                  AttributeDefinitionBroker, AttributeDefinition
from ce1sus.web.helpers.protection import require
from cherrypy._cperror import HTTPRedirect
from framework.helpers.rt import RTHelper
import types
from framework.db.broker import NothingFoundException, ValidationException, \
BrokerException
from framework.helpers.converters import ObjectConverter
from ce1sus.web.helpers.protection import privileged
class TicketsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.def_objectBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)
    self.commentBroker = self.brokerFactory(CommentBroker)
    self.ticketBroker = self.brokerFactory(TicketBroker)


  @cherrypy.expose
  @require()
  def tickets(self, eventID):
    """
    Lists all event tickets and tickets
    """
    template = self.mako.getTemplate('/events/event/tickets/tickets.html')
    event = self.eventBroker.getByID(eventID)

    # right checks
    self.checkIfViewable(event.groups, self.getUser().identifier ==
                         event.creator.identifier)


    ticketLabels = [{'identifier':'#'},
              {'ticket':'Ticket Number'},
              {'creator.username':'Created by'},
              {'created':'CreatedOn'}]

    paginatorOptions = PaginatorOptions('/events/event/tickets/tickets/{0}'.format(eventID), 'eventTabs{0}TabContent'.format(eventID))
    paginatorOptions.addOption('DIALOG', 'REMOVE', '/events/event/tickets/modifyTicket?action=remove&eventID={0}&ticketID='.format(eventID), contentid='', refresh=True)



    ticketPaginator = Paginator(items=event.tickets,
                          labelsAndProperty=ticketLabels,
                          paginatorOptions=paginatorOptions)



    return template.render(eventID=eventID,
                           ticketPaginator=ticketPaginator,
                           rtUrl=RTHelper.getInstance().getTicketUrl())

  @cherrypy.expose
  @require()
  def getRTTable(self):
    template = self.mako.getTemplate('/events/event/tickets/RTTable.html')

    # the labels etc is handeled by the RTTable.html
    rtPaginator = Paginator(items=RTHelper.getInstance().getAllTickets(),
                          labelsAndProperty=None)
    return template.render(rtPaginator=rtPaginator,
                           rtUrl=RTHelper.getInstance().getTicketUrl())

  @cherrypy.expose
  @require()
  def modifyTicket(self,
                        eventID,
                        action,
                        ticketTable_length=None,
                        tickets=None,
                        ticketID=None):
    """
    Processes the modifications of an event
    """
    event = self.eventBroker.getByID(eventID)

    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)
    try:
      if action == 'insert':
      # create and insert tickets

        if not tickets is None:
          if isinstance(tickets, types.StringTypes):
            ticket = Ticket()
            ticket.identifier = None
            ticket.created = datetime.now()
            ticket.ticket = tickets
            ticket.creator = self.getUser()
            ticket.user_id = ticket.creator.identifier
            ticket.events.append(event)
            self.ticketBroker.insert(ticket)
          else:
            for ticketID in tickets:
              # fillup tickets
              ticket = Ticket()
              ticket.identifier = None
              ticket.created = datetime.now()
              ticket.ticket = ticketID
              ticket.creator = self.getUser()
              ticket.user_id = ticket.creator.identifier
              ticket.events.append(event)
              self.ticketBroker.insert(ticket, False)
            # commit when all are set up
            self.ticketBroker.session.commit()
      if action == 'remove':
        ticket = self.ticketBroker.getByID(ticketID);
        event.removeTicket(ticket)

      return self.returnAjaxOK()
    except BrokerException as e:
      self.getLogger().critical(e)

          # update last_seen
    # TODO update event
    # self.updateEvent(event)




