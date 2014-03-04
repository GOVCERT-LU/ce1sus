# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.common.handlers.generichandler import GenericHandler


class DateHandler(GenericHandler):
  """The generic handler for handling known atomic values"""

  @staticmethod
  def get_uuid():
    return '11406d00-8dec-11e3-baa8-0800200c9a66'

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    return template_renderer('/common/handlers/datetime.html',
                             attribute=None,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)

  def render_gui_view(self, template_renderer, attribute, user):
    return template_renderer('/common/handlers/datetime.html',
                             attribute=attribute,
                             enabled=False,
                             default_share_value=0,
                             enable_share=False)

  # pylint: disable=R0913,W0613
  def render_gui_edit(self, template_renderer, attribute, additional_attributes, share_enabled):
    return template_renderer('/common/handlers/datetime.html',
                             attribute=attribute,
                             enabled=True,
                             default_share_value=0,
                             enable_share=share_enabled)
