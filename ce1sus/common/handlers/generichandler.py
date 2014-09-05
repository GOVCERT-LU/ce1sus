# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Aug 22, 2013
"""


from ce1sus.brokers.event.eventclasses import Attribute
from ce1sus.common.handlers.base import HandlerBase, UndefinedException
from ce1sus.helpers.bitdecoder import BitValue
from dagr.helpers.converters import ObjectConverter
from dagr.helpers.datumzait import DatumZait
import uuid as uuidgen
from ce1sus.brokers.event.eventclasses import Object


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'



class GenericHandler(HandlerBase):
  """The generic handler for handling known atomic values"""

  @staticmethod
  def get_uuid():
    return 'dea62bf0-8deb-11e3-baa8-0800200c9a66'

  def get_additional_object_chksums(self):
    return list()

  @staticmethod
  def get_allowed_types():
    return [0, 1, 3]

  @staticmethod
  def create_object(parent, definition, user, group, share=None):
    obj = Object()
    obj.bit_value = BitValue('0', obj)
    if share is None:
      # use the default value from the definition
      if definition.share == 1:
        obj.bit_value.is_shareable = True
      else:
        obj.bit_value.is_shareable = False
    else:
      # check if parent is sharable
      if parent.bit_value.is_shareable:
        if share == '0':
          obj.bit_value.is_shareable = False
        else:
          obj.bit_value.is_shareable = True
      else:
        obj.bit_value.is_shareable = False

    obj.identifier = None
    obj.uuid = unicode(uuidgen.uuid4())
    obj.definition = definition
    obj.created = DatumZait.utcnow()
    obj.modified = DatumZait.utcnow()
    obj.creator = user
    obj.creator_id = user.identifier
    obj.modifier_id = user.identifier
    obj.modifier = user
    obj.creator = user
    obj.event = parent.event

    if group:
      obj.creator_group_id = group.identifier
    else:
      obj.creator_group_id = user.default_group.identifier

      return obj

  @staticmethod
  def create_attribute(params, obj, definition, user, group):
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
    attribute.uuid = unicode(uuidgen.uuid4())
    value = params.get('value', None)
    share = params.get('shared', None)
    attribute.bit_value = BitValue('0', attribute)
    if share is None:
      # use the default value from the definition
      if definition.share == 1:
        attribute.bit_value.is_shareable = True
      else:
        attribute.bit_value.is_shareable = False
    else:
      # check if parent is sharable
      if obj.bit_value.is_shareable:
        if share == '0':
          attribute.bit_value.is_shareable = False
        else:
          attribute.bit_value.is_shareable = True
      else:
        attribute.bit_value.is_shareable = False

    is_ioc = params.get('ioc', None)
    if is_ioc is None:
      # take default value
      attribute.ioc = 0
    else:
      ObjectConverter.set_integer(attribute, 'ioc', is_ioc)

    # Note first the definition has to be specified
    attribute.definition = definition
    attribute.def_attribute_id = definition.identifier

    # Note second the object has to be specified
    attribute.object = obj
    attribute.object_id = obj.identifier

    GenericHandler.set_value_to_attr(attribute, value)

    attribute.definition = definition
    attribute.created = DatumZait.utcnow()
    attribute.modified = DatumZait.utcnow()
    attribute.creator = user
    attribute.creator_id = user.identifier
    attribute.modifier_id = user.identifier
    attribute.modifier = user
    attribute.creator = user

    if group:
      attribute.creator_group_id = group.identifier
    else:
      attribute.creator_group_id = user.default_group.identifier

    return attribute

  @staticmethod
  def set_value_to_attr(attribute, value):
    if isinstance(value, list):
      value = value[0]
    if hasattr(value, 'strip'):
      attribute.value = value.strip()
    else:
      attribute.value = value

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

  def render_gui_edit(self, template_renderer, attribute, additional_attributes, share_enabled):
    if attribute.bit_value.is_shareable:
      default_share_value = '1'
    else:
      default_share_value = '0'
    return template_renderer('/common/handlers/generic.html',
                             attribute=attribute,
                             enabled=True,
                             default_share_value=default_share_value,
                             enable_share=share_enabled)

  def process_gui_post(self, obj, definitions, user, params):
    action = params.get('action', None)
    if action:
      if action == 'insert':
        definition = self._get_main_definition(definitions)
        attribute = self.create_attribute(params, obj, definition, user, None)
        return attribute, None
      elif action == 'update':
        attribute = params.get('attribute', None)
        if attribute:
          value = params.get('value', None)
          GenericHandler.set_value_to_attr(attribute, value)
          return attribute, None
        else:
          raise UndefinedException(u'Attribute is not defined')
      else:
        raise UndefinedException(u'Action {0} is not defined'.format(action))

  def get_additinal_attribute_chksums(self):
    return list()

  def convert_to_rest_value(self, attribute):
    value = attribute.plain_value
    return value

  def process_rest_post(self, obj, definitions, user, group, params):
    definition = self._get_main_definition(definitions)
    attribute = self.create_attribute(params, obj, definition, user, group)
    return attribute, None
