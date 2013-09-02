from ce1sus.web.helpers.handlers.generichandler import GenericHandler
from ce1sus.brokers.eventbroker import Attribute
import types
from ce1sus.api.ticketsystem import TicketSystemBase
from framework.web.helpers.config import WebConfig
from framework.web.helpers.pagination import Link
from ce1sus.web.helpers.handlers.base import HandlerException
import copy

class TicketHandler(GenericHandler):

  def __init__(self):
    GenericHandler.__init__(self)
    self.url = TicketSystemBase.getInstance().getBaseTicketUrl()

  def populateAttributes(self, params, obj, definition, user):
    # check if params contains value
    if params.has_key('value'):
      attributes = list()
      attribute = GenericHandler.populateAttributes(self, params, obj, definition, user)
      attributes.append(attribute)
      return attributes
    else:
      if params.has_key('tickets'):
        tickets = params.get('tickets');
        attributes = list()
        if isinstance(tickets, types.StringTypes):
          params['value'] = tickets
          attribute = GenericHandler.populateAttributes(self, params, obj, definition, user)
          attributes.append(attribute)
        else:
          for ticket in tickets:
            params['value'] = ticket
            attribute = GenericHandler.populateAttributes(self, params, obj, definition, user)
            attributes.append(attribute)
        return attributes
      else:
        raise HandlerException('Noting entered!!!')

    # check if params contains tickets


  def render(self, enabled, attribute=None):
    template = self.getTemplate('/events/event/attributes/handlers/ticket.html')
    string = template.render(attribute=attribute, enabled=enabled)
    return string

  def convertToAttributeValue(self, value):
    link = Link(self.url, value.value)
    return link

class CVEHandler(GenericHandler):

  def __init__(self):
    GenericHandler.__init__(self)
    self.url = WebConfig.getInstance().get('cveurl')

  def render(self, enabled, attribute=None):
    template = self.getTemplate('/events/event/attributes/handlers/cve.html')
    string = template.render(attribute=attribute, enabled=enabled)
    return string

  def convertToAttributeValue(self, value):
    link = Link(self.url, value.value)
    return link
