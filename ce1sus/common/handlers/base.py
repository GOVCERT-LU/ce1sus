# -*- coding: utf-8 -*-

"""
module providing support for the base handler

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
from ce1sus.web.views.helpers.tabs import ModalOption, YesNoDialogOption
from ce1sus.common.system import put_to_array


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

  def __default_handler_view_options(self, event_id, obj_id, attr_id):
    eye = ModalOption(title=u'Attribute #{0} Details'.format(attr_id),
                      owner_option=False,
                      attribute_owner_option=False,
                      refresh=False,
                      position=0,
                      icon_name='glyphicon glyphicon-eye-open',
                      post_url=None,
                      content_url='/events/event/attribute/view/{0}/{1}/{2}'.format(event_id, obj_id, attr_id),
                      description='View details'
                      )
    pencil = ModalOption(title=u'Edit Attribute #{0}'.format(attr_id),
                      owner_option=True,
                      attribute_owner_option=True,
                      refresh=True,
                      position=1,
                      icon_name='glyphicon glyphicon-pencil',
                      post_url='/events/event/attribute/call_handler_post',
                      content_url='/events/event/attribute/edit/{0}/{1}/{2}'.format(event_id, obj_id, attr_id),
                      description='Modify Attribute'
                      )
    validation = YesNoDialogOption(owner_option=True,
                               validation_option=True,
                               attribute_owner_option=False,
                               refresh=True,
                               position=-1,
                               icon_name='glyphicon glyphicon-saved',
                               message=u'Are you sure you want to validate Attribute #{0}?'.format(attr_id),
                               post_url=u'/events/event/attribute/validate_attribute?event_id={0}&attribute_id={1}'.format(event_id, attr_id),
                               description='Validate Attribute')
    remove = YesNoDialogOption(owner_option=True,
                               attribute_owner_option=True,
                               refresh=True,
                               position=None,
                               icon_name='glyphicon glyphicon-remove-circle',
                               message=u'Are you sure you want to delete Attribute #{0}?'.format(attr_id),
                               post_url=u'/events/event/attribute/remove_attribute?event_id={0}&attribute_id={1}'.format(event_id, attr_id),
                               description='Remove Attribute')
    return [eye, pencil, remove, validation]

  def handler_view_options(self, event_id, obj_id, attr_id):
    return None

  def get_ordered_view_options(self, event_id, obj_id, attr_id):
    result = list()

    for option in self.__default_handler_view_options(event_id, obj_id, attr_id):
      put_to_array(result, option.position, option)
    additional_options = self.handler_view_options(event_id, obj_id, attr_id)
    if additional_options:
      for option in additional_options:
        put_to_array(result, option.position, option)
    return result

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
