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


class MultipleGenericHandler(GenericHandler):

  def process_gui_post(self, obj, definitions, user, params):
    definition = self._get_main_definition(definitions)
    attributes = list()
    values = params.get('value').split('\n')
    for value in values:
      params['value'] = value
      attribute = self.create_attribute(params, obj, definition, user)
      attributes.append(attribute)
    attribute = attributes.pop(0)
    return attribute, attributes

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    return template_renderer('/common/handlers/multGeneric.html',
                             attribute=None,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)
