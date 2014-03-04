# -*- coding: utf-8 -*-

"""
module providing support for tickets handling

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.common.handlers.generichandler import GenericHandler
import types
from dagr.helpers.rt import RTTickets
from ce1sus.common.handlers.base import HandlerException
from dagr.web.views.classes import Link


class RTHandler(GenericHandler):
  """Handler for handling tickets"""
  def __init__(self, config):
    GenericHandler.__init__(self, config)
    self.rt_system = RTTickets(self.config.get('rt_url'),
                        self.config.get('rt_user'),
                        self.config.get('rt_password'))

  @staticmethod
  def get_uuid():
    return 'f1509d30-8deb-11e3-baa8-0800200c9a66'

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    return template_renderer('/common/handlers/ticket.html',
                             attribute=None,
                             enabled=True,
                             default_share_value=0,
                             enable_share=False,
                             definition_id=definition.identifier)

  def process_gui_post(self, obj, definitions, user, params):
    # check if params contains value
    params['ioc'] = '0'
    params['shared'] = '0'
    definition = self._get_main_definition(definitions)
    values = params.get('value', None)
    if values:
      value_arry = values.split(',')
      if len(value_arry) == 1:
        attribute = GenericHandler.create_attribute(params,
                                                    obj,
                                                    definition,
                                                    user)
        return attribute, None
      else:
        attributes = list()
        first = True
        for value in value_arry:
          params['value'] = value
          attribute = GenericHandler.create_attribute(params,
                                                  obj,
                                                  definition,
                                                  user)
          if first:
            main_attribute = attribute
            first = False
          else:
            attributes.append(attribute)
        return main_attribute, attributes
    else:
      raise HandlerException('Please select something before saveing.')

  def render_gui_view(self, template_renderer, attribute, user):
    # convert attribute's value
    return template_renderer('/common/handlers/ticket.html',
                             attribute=attribute,
                             enabled=False,
                             default_share_value=0,
                             enable_share=False,
                             definition_id=attribute.definition.identifier)

  def render_gui_get(self, template_renderer, action, attribute, user):
    """
    renders the file for displaying the tickets out of RT

    :returns: generated HTML
    """
    tickets = self.rt_system.get_all_tickets()
    return template_renderer('/common/handlers/RTtickets.html',
                             tickets=tickets,
                             rt_url=self.rt_system.get_base_ticket_url())

  def convert_to_gui_value(self, attribute):
    link = Link()
    link.url_base = self.rt_system.get_base_ticket_url()
    link.identifier = attribute.plain_value
    return link


class CVEHandler(GenericHandler):
  """Handler for handling cves"""

  def __init__(self, config):
    GenericHandler.__init__(self, config)
    self.url = self.config.get('cveurl')

  @staticmethod
  def get_uuid():
    return '04cda0b0-8dec-11e3-baa8-0800200c9a66'

  def render_gui_view(self, template_renderer, attribute, user):
    # convert attribute's value
    return template_renderer('/common/handlers/cve.html',
                             attribute=attribute,
                             enabled=False,
                             default_share_value=0,
                             enable_share=False)

  def convert_to_gui_value(self, attribute):
    link = Link()
    link.url_base = self.url
    link.identifier = attribute.plain_value
    return link


class LinkHander(GenericHandler):
  """Handler for handling Links"""

  @staticmethod
  def get_uuid():
    return '1e18d8f0-8dec-11e3-baa8-0800200c9a66'

  def convert_to_gui_value(self, attribute):
    link = Link()
    link.url_base = ''
    link.identifier = attribute.plain_value
    return link
