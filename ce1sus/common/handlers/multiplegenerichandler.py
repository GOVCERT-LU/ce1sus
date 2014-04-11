# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Sep 19, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.common.handlers.generichandler import GenericHandler
import types
from ce1sus.common.handlers.base import HandlerException


class MultipleGenericHandler(GenericHandler):

  @staticmethod
  def get_uuid():
    return '08645c00-8dec-11e3-baa8-0800200c9a66'

  def __get_string_attribtues(self, params):
    return params.get('value').split('\n')

  def __get_list_attribtues(self, params):
    return params.get('value')

  def process_gui_post(self, obj, definitions, user, params):
    definition = self._get_main_definition(definitions)
    attributes = list()
    value = params.get('value')
    # the value can either be a list or a string
    if isinstance(value, types.StringTypes):
      values = self.__get_string_attribtues(params)
    else:
      values = self.__get_list_attribtues(params)
    if value:
      for value in values:
        value = value.strip('\n\r')
        if value:
          params['value'] = value
          attribute = self.create_attribute(params, obj, definition, user)
          attributes.append(attribute)
      attribute = attributes.pop(0)
      return attribute, attributes
    else:
      raise HandlerException('No attribute specified. Please Try again.')

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    return template_renderer('/common/handlers/multGeneric.html',
                             attribute=None,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)

  def render_gui_edit(self, template_renderer, attribute, additional_attributes, share_enabled):
    # Combine all attributes into one
    attribtues = list()
    if additional_attributes:
      attribtues += additional_attributes
      attribtues.insert(0, attribute)
    else:
      attribtues.append(attribute)
    if attribute.bit_value.is_shareable:
      default_share_value = '1'
    else:
      default_share_value = '0'
    return template_renderer('/common/handlers/multGenericEdit.html',
                             attributes=attribtues,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)
