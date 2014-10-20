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


class UndefinedException(HandlerException):
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

    :param template_renderer: template renderer
    :type template_renderer: Makohandler
    :param action: Action used to call
    :type action: String
    :param attribute: The attribute in context
    :type attribute: Attribute
    :param user: The user calling the function
    :type user: User

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
    Process of the post over the GUI

    :param obj: parent object
    :type obj: Object
    :param definitions: The reqiried definitions
    :type definitions: List of attribtue Definitions
    :param user: The user calling the function
    :type user: User
    :param params: The parameters of the post
    :type params: Dict

    :returns: Attribute, [List of Attribute]
    """
    raise HandlerException(('process_gui_post not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       params,
                                                       user,
                                                       obj,
                                                       definitions))

  @staticmethod
  def get_uuid():
    raise HandlerException('get_uuid not defined')

  @staticmethod
  def get_allowed_types():
    raise HandlerException('get_allowed_types not defined')

  def render_gui_view(self, template_renderer, attribute, user):
    """
    Generates the HTML for displaying the attribute

    :param template_renderer: template renderer
    :type template_renderer: Makohandler
    :param attribute: The attribute to be displayed
    :type attribute: Attribute
    :param attribute: The attribute in context
    :type attribute: Attribute
    :param user: The user calling the function
    :type user: User


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

    :param template_renderer: template renderer
    :type template_renderer: Makohandler
    :param definition: The attribute to be displayed
    :type definition: AttributeDefinition
    :param default_share_value: The value for the default share
    :type default_share_value: Boolean
    :param share_enabled: should the share be enabled
    :type share_enabled: Boolean

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

    :param template_renderer: template renderer
    :type template_renderer: Makohandler
    :param attribute: The attribute to be displayed
    :type attribute: Attribute
    :param additional_attributes: Action used to call
    :type additional_attributes: String
    :param user: The user calling the function
    :type user: User

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

  def convert_to_rest_value(self, attribute):
    """
    Converts the value suited for rest elements
    """
    raise HandlerException(('convert_to_rest_value not defined for {0} with parameters '
                           + '{1}').format(self.__class__.__name__, attribute))

  def get_additinal_attribute_chksums(self):
    """
    Returns a list of additional attributes checksums required for the handling
    """
    raise HandlerException(('get_additinal_attribute_chksums not defined for {0}').format(self.__class__.__name__))

  def get_additional_object_chksums(self):
    raise HandlerException(('get_additional_object_chksums not defined for {0}').format(self.__class__.__name__))

  def _get_main_definition(self, definitions):
    """
    Returns the definition using this handler
    """
    chksums = self.get_additinal_attribute_chksums() + self.get_additional_object_chksums()
    diff = list(set(definitions.keys()) - set(chksums))
    if len(diff) == 1:
      main_definition = definitions.get(diff[0], None)
      if main_definition:
        return main_definition
      else:
        raise HandlerException((u'Error determining main definition for {0}').format(self.__class__.__name__))
    else:
      raise HandlerException((u'Could not determine main definition for {0}').format(self.__class__.__name__))

  def process_rest_post(self, obj, definitions, user, group, rest_attribute):
    """
    Process of the post over the RestAPI

    :param obj: parent object
    :type obj: Object
    :param definitions: The reqiried definitions
    :type definitions: List of attribtue Definitions
    :param user: The user calling the function
    :type user: User
    :param rest_attribute: Attribute inserting over rest
    :type rest_attribute: ReatAttribue

    :returns: Attribute, [List of Attribute]
    """
    raise HandlerException(('process_gui_post not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       obj,
                                                       definitions,
                                                       user,
                                                       group,
                                                       rest_attribute))
