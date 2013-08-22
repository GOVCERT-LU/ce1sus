"""module holding all controllers needed for the event handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.web.controllers.base import BaseController
import cherrypy
from framework.web.helpers.pagination import Paginator, PaginatorOptions
from datetime import datetime
from ce1sus.brokers.eventbroker import EventBroker, Ticket, TicketBroker
from ce1sus.web.helpers.protection import require
from framework.helpers.rt import RTHelper
import types
from framework.db.broker import BrokerException
class TicketsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.ticketBroker = self.brokerFactory(TicketBroker)


  @cherrypy.expose
  @require()
  def tickets(self, eventID):
    """
    Lists all event tickets and tickets

    :returns: generated HTML
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

    paginatorOptions = PaginatorOptions(('/events/event/'
                                         + 'tickets/tickets/{0}').format(
                                                                      eventID),
                                        'eventTabs{0}TabContent'.format(
                                                                      eventID))
    paginatorOptions.addOption('DIALOG',
                               'REMOVE',
                               ('/events/event/tickets/modifyTicket'
                                + '?action=remove&eventID={0}&'
                                + 'ticketID=').format(eventID),
                               contentid='',
                               refresh=True)



    ticketPaginator = Paginator(items=event.tickets,
                          labelsAndProperty=ticketLabels,
                          paginatorOptions=paginatorOptions)



    return template.render(eventID=eventID,
                           ticketPaginator=ticketPaginator,
                           rtUrl=RTHelper.getInstance().getTicketUrl())

  @cherrypy.expose
  @require()
  def getRTTable(self):
    """
    renders the file for displaying the tickets out of RT

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/event/tickets/RTTable.html')

    # the labels etc is handled by the RTTable.html
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
            events = getattr(ticket, 'events')
            function = getattr(events, 'append')
            function(event)
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
              events = getattr(ticket, 'events')
              function = getattr(events, 'append')
              function(event)
              self.ticketBroker.insert(ticket, False)
            # commit when all are set up
            self.ticketBroker.session.commit()
      if action == 'remove':
        ticket = self.ticketBroker.getByID(ticketID)
        event.removeTicket(ticket)
          # update last_seen
          # TODO update event
          # self.updateEvent(event)
      return self.returnAjaxOK()
    except BrokerException as e:
      self.getLogger().critical(e)






