# -*- coding: utf-8 -*-

"""
module providing support for tickets handling

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.helpers.handlers.generichandler import GenericHandler
import types
from dagr.helpers.classes.ticketsystem import TicketSystemBase
from dagr.web.helpers.config import WebConfig
from dagr.web.helpers.pagination import Link
from ce1sus.web.helpers.handlers.base import HandlerException


class TicketHandler(GenericHandler):
  """Handler for handling tickets"""
  def __init__(self):
    GenericHandler.__init__(self)
    self.url = TicketSystemBase.getInstance().getBaseTicketUrl()

  def populateAttributes(self, params, obj, definition, user):
    # check if params contains value
    if 'value' in params:
      attributes = list()
      attribute = GenericHandler.populateAttributes(self,
                                                    params,
                                                    obj,
                                                    definition,
                                                    user)
      attributes.append(attribute)
      return attributes
    else:
      if 'tickets' in params:
        tickets = params.get('tickets')
        attributes = list()
        if isinstance(tickets, types.StringTypes):
          params['value'] = tickets
          attribute = GenericHandler.populateAttributes(self,
                                                        params,
                                                        obj,
                                                        definition,
                                                        user)
          attributes.append(attribute)
        else:
          for ticket in tickets:
            params['value'] = ticket
            attribute = GenericHandler.populateAttributes(self,
                                                          params,
                                                          obj,
                                                          definition,
                                                          user,
                                                    '0')
            attributes.append(attribute)
        return attributes
      else:
        raise HandlerException('Noting entered!!!')

    # check if params contains tickets

  def render(self, enabled, eventID, user, definition, attribute=None):
    template = self.getTemplate('/events/event/attributes/handlers/ticket.html'
                                )
    string = template.render(attribute=attribute, enabled=enabled)
    return string

  def convertToAttributeValue(self, value):
    link = Link(self.url, value.value)
    return link


class CVEHandler(GenericHandler):
  """Handler for handling cves"""
  def __init__(self):
    GenericHandler.__init__(self)
    self.url = WebConfig.getInstance().get('cveurl')

  def render(self, enabled, eventID, user, definition, attribute=None):
    template = self.getTemplate('/events/event/attributes/handlers/cve.html')
    if definition.share:
      defaultShareValue = 1
    else:
      defaultShareValue = 0

    return template.render(attribute=attribute,
                             enabled=enabled,
                             defaultShareValue=defaultShareValue)

  def convertToAttributeValue(self, value):
    link = Link(self.url, value.value)
    return link
