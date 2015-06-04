# -*- coding: utf-8 -*-

"""
module providing support for tickets handling

Created: Aug, 2013
"""
from ce1sus.handlers.references.generichandler import GenericHandler
from ce1sus.helpers.common.rt import RTTickets
from ce1sus.handlers.base import HandlerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RTHandler(GenericHandler):
  """Handler for handling tickets"""
  def __init__(self):
    GenericHandler.__init__(self)
    url = self.get_config_value('rt_url', None)
    usr = self.get_config_value('rt_user', None)
    pwd = self.get_config_value('rt_password', None)
    if url is None or usr is None or pwd is None:
      raise HandlerException(u'RT handler is not configured.')
    self.rt_system = RTTickets(url, usr, pwd)

  @staticmethod
  def get_uuid():
    return 'f1509d30-8deb-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Handler for RT Tickets'

  def __convert_ticket_to_dict(self, ticket):
    return {'identifier': ticket.identifier,
            'title': ticket.title,
            'url': ticket.url
            }

  def get_data(self, reference_uuid, definition, parameters):
    type_ = parameters.get('type', 'view')
    if type_ == 'view':
      return [self.rt_system.get_base_ticket_url()]
    else:
      tickets = self.rt_system.get_all_tickets()
      # convert the tickets into dictionaries
      result = list()
      for ticket in tickets:
        result.append(self.__convert_ticket_to_dict(ticket))
      return result

  def get_view_type(self):
    return 'rtticket'

  def require_js(self):
    return True
