# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.common.handlers.base import HandlerException
from ce1sus.common.handlers.generichandler import GenericHandler
from dagr.helpers.validator.valuevalidator import ValueValidator


class CBValueHandler(GenericHandler):
  """The generic handler for handling known atomic values"""

  @staticmethod
  def get_uuid():
    return '141dea70-8dec-11e3-baa8-0800200c9a66'

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    cb_values = CBValueHandler.__get_cb_values(definition.regex)
    return template_renderer('/common/handlers/cbValues.html',
                             cb_values=cb_values,
                             attribute=None,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)

  def render_gui_view(self, template_renderer, attribute, user):
    cb_values = CBValueHandler.__get_cb_values(attribute.definition.regex)
    return template_renderer('/common/handlers/cbValues.html',
                             cb_values=cb_values,
                             attribute=attribute,
                             enabled=False,
                             default_share_value=0,
                             enable_share=False)

  # pylint: disable=R0913,W0613
  def render_gui_edit(self, template_renderer, attribute, additional_attributes, share_enabled):
    cb_values = CBValueHandler.__get_cb_values(attribute.definition.regex)
    return template_renderer('/common/handlers/cbValues.html',
                             cb_values=cb_values,
                             attribute=attribute,
                             enabled=True,
                             default_share_value=0,
                             enable_share=share_enabled)

  @staticmethod
  def __check_vailidity_regex(regex):
    """
    Checks if the regular expression is under the correct form
    """
    val_regex = r'^(?:\^.+\$\|)+(?:\^.+\$)$'
    valid = ValueValidator.validateRegex(regex,
                                         val_regex,
                                         '')
    if not valid:
      raise HandlerException(('The regular expression of the definition is invalid.\n'
                              + 'It should be under the form of:\n{0}\n'
                              + 'Please fix the definition before using this definition.'
                              ).format(val_regex))

  @staticmethod
  def __get_cb_values(regex):
    """
    Returns the combo box values
    """
    result = dict()
    CBValueHandler.__check_vailidity_regex(regex)
    items = regex.split('|')
    for item in items:
      temp = item.replace('$', '')
      temp = temp.replace('^', '')
      result[temp] = temp
    return result
