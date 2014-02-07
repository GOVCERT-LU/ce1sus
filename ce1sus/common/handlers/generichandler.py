# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.common.handlers.base import HandlerBase
from ce1sus.brokers.event.eventclasses import Attribute
from dagr.helpers.datumzait import DatumZait
from dagr.helpers.converters import ObjectConverter
from ce1sus.helpers.bitdecoder import BitValue


class GenericHandler(HandlerBase):
  """The generic handler for handling known atomic values"""

  @staticmethod
  def create_attribute(params, obj, definition, user):
    """
    Creates the attribute

    :param params: The parameters
    :type params: Dictionary
    :param obj: The object the attributes belongs to
    :type obj: BASE object
    :param definition: Attribute definition
    :type definition: AttributeDefinition
    :param user: The user creating the attribute
    :type user: User

    :returns: Attribute
    """
    attribute = Attribute()
    attribute.identifier = None
    value = params.get('value')
    share = params.get('shared')
    if isinstance(value, list):
      value = value[0]
    if hasattr(value, 'strip'):
      attribute.value = value.strip()
    else:
      attribute.value = value
    attribute.obejct = obj
    attribute.object_id = obj.identifier
    attribute.definition = definition
    attribute.def_attribute_id = definition.identifier
    attribute.definition = definition
    attribute.created = DatumZait.utcnow()
    attribute.modified = DatumZait.utcnow()
    attribute.creator = user
    attribute.creator_id = user.identifier
    attribute.modifier_id = user.identifier
    attribute.modifier = user
    attribute.creator = user
    ObjectConverter.set_integer(attribute,
                               'ioc',
                               params.get('ioc', '0').strip())
    attribute.bit_value = BitValue('0', attribute)
    # check if parent is sharable
    if obj.bit_value.is_shareable:
      if share == '1':
        attribute.bit_value.is_shareable = True
      else:
        attribute.bit_value.is_shareable = False
    else:
      attribute.bit_value.is_shareable = False
    return attribute

  def render_gui_input(self, template_renderer, definition, default_share_value, share_enabled):
    return template_renderer('/common/handlers/generic.html',
                             attribute=None,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)

  def convert_to_gui_value(self, attribute):
    return attribute.plain_value

  def render_gui_view(self, template_renderer, attribute, user):
    # convert attribute's value
    return template_renderer('/common/handlers/generic.html',
                             attribute=attribute,
                             enabled=False,
                             default_share_value=0,
                             enable_share=False)

  def render_gui_edit(self, template_renderer, attribute, default_share_value, share_enabled):
    return template_renderer('/common/handlers/generic.html',
                             attribute=attribute,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)

  def process_gui_post(self, obj, definitions, user, params):
    definition = self._get_main_definition(definitions)
    attribute = self.create_attribute(params, obj, definition, user)
    return attribute, None

  def get_additinal_attribute_chksums(self):
    return list()

  def convert_to_rest_value(self, attribute, config):
    return attribute.plain_value
