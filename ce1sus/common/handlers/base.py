# -*- coding: utf-8 -*-

"""
module providing support for the base handler

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class HandlerException(Exception):
  """
  Exception base for handler exceptions
  """
  pass


class HandlerBase(object):
  """
  Base class for handlers

  Note this class is pseudo abstract
  """
  def __init__(self, config):
    self.config = config

  def render_gui_get(self, template_renderer, action, attribute, user):
    """
    Generates the HTML for an external get method

    :param enabled: If the view should be enabled
    :type enabled: Boolean
    :param attribute: The attribute to be displayed
    :type attribute: Attribute

    :returns: generated HTML
    """
    raise HandlerException(('render_gui_get not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       template_renderer,
                                                       attribute,
                                                       user,
                                                       action))

  def process_gui_post(self, obj, definitions, user, params):
    """
    Generates the HTML for an external get method

    :param enabled: If the view should be enabled
    :type enabled: Boolean
    :param attribute: The attribute to be displayed
    :type attribute: Attribute

    :returns: Attribute, [List of Attribute]
    """
    raise HandlerException(('process_gui_post not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       params,
                                                       user,
                                                       obj,
                                                       definitions))

  def render_gui_view(self, template_renderer, attribute, user):
    """
    Generates the HTML for displaying the attribute

    :param enabled: If the view should be enabled
    :type enabled: Boolean
    :param attribute: The attribute to be displayed
    :type attribute: Attribute

    :returns: generated HTML
    """
    raise HandlerException(('render_gui_view not defined for {0} with parameters '
                           + '{1},{2},{3}').format(self.__class__.__name__,
                                                       template_renderer,
                                                       attribute,
                                                       user))

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    """
    Generates the HTML for displaying the attribute

    :param enabled: If the view should be enabled
    :type enabled: Boolean
    :param attribute: The attribute to be displayed
    :type attribute: Attribute

    :returns: generated HTML
    """
    raise HandlerException(('render_gui_input not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       template_renderer,
                                                       default_share_value,
                                                       share_enabled,
                                                       definition))

  # pylint: disable=R0913
  def render_gui_edit(self, template_renderer, attribute, additional_attributes, share_enabled):
    """
    Generates the HTML for displaying the attribute

    :param enabled: If the view should be enabled
    :type enabled: Boolean
    :param attributes: The attribute to be displayed
    :type attribute: List of Attribute

    :returns: generated HTML
    """
    raise HandlerException(('render_gui_edit not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       template_renderer,
                                                       attribute,
                                                       additional_attributes,
                                                       share_enabled))

  def convert_to_gui_value(self, attribute):
    """
    Converts the attribute suited for GUI elements
    """
    raise HandlerException(('convert_to_gui_value not defined for {0} with parameters '
                           + '{1}').format(self.__class__.__name__, attribute))

  def convert_to_search_value(self, value, config):
    """
    Converts the search value to be suited for GUI elements

    NOTE: USE ONLY VALUE HERE!!!!
    """
    raise HandlerException(('convert_to_search_value not defined for {0} with parameters '
                           + '{1},{2}').format(self.__class__.__name__, value, config))

  def convert_to_rest_value(self, attribute, config):
    """
    Converts the value suited for rest elements
    """
    raise HandlerException(('convert_to_rest_value not defined for {0} with parameters '
                           + '{1},{2}').format(self.__class__.__name__, attribute, config))

  def convert_to_rest_value_to_plain(self, value, config):
    """
    Converts the value suited for rest elements
    """
    raise HandlerException(('convert_to_rest_value not defined for {0} with parameters '
                           + '{1},{2}').format(self.__class__.__name__, value, config))

  def get_additinal_attribute_chksums(self):
    """
    Returns a list of additional attributes checksums required for the handling
    """
    raise HandlerException(('get_additinal_attribute_chksums not defined for {0}').format(self.__class__.__name__))

  def _get_main_definition(self, definitions):
    """
    Returns the definition using this handler
    """
    chksums = self.get_additinal_attribute_chksums()
    diff = list(set(definitions.keys()) - set(chksums))
    if len(diff) == 1:
      main_definition = definitions.get(diff[0], None)
      if main_definition:
        return main_definition
      else:
        raise HandlerException('Error determining main definition for {0}').format(self.__class__.__name__)
    else:
      raise HandlerException('Could not determine main definition for {0}').format(self.__class__.__name__)
