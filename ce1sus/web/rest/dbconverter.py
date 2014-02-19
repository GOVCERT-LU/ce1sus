# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 6, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.helpers.debug import Log
from ce1sus.api.restclasses import RestEvent, RestObject, RestAttribute, RestObjectDefinition, RestAttributeDefinition
from ce1sus.brokers.event.eventclasses import Event, Object, Attribute
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition, AttributeDefinition
from ce1sus.common.handlers.base import HandlerException
from ce1sus.controllers.event.event import EventController
from ce1sus.controllers.event.objects import ObjectsController
from ce1sus.controllers.event.attributes import AttributesController
from dagr.controllers.base import ControllerException
from dagr.helpers.hash import hashMD5


class DBConversionException(Exception):
  """Base exception for this class"""
  pass


class DBConverter(object):

  """Class is in charge of converting DB Objects to Rest Objects"""

  def __init__(self, config):
    self.__config = config
    self.logger = Log(config)
    self.event_controller = EventController(config)
    self.object_controller = ObjectsController(config)
    self.attribtue_controller = AttributesController(config)

  def _get_logger(self):
    """Returns the class logger"""
    return self.logger.get_logger(self.__class__.__name__)

  def convert_event(self, event, owner, full, with_definition):
    """Converts Event to RestEvent"""
    self._get_logger().debug('Converting event')
    rest_event = RestEvent()
    rest_event.title = event.title
    rest_event.description = event.description
    rest_event.first_seen = event.first_seen
    rest_event.last_seen = event.last_seen
    rest_event.tlp = event.tlp.text
    rest_event.risk = event.risk
    rest_event.analysis = event.analysis
    rest_event.status = event.status
    rest_event.uuid = event.uuid
    rest_event.published = event.published
    rest_event.group = event.creator_group.name
    rest_event.objects = list()
    if full:
      for obj in event.objects:
        # share only the objects which are shareable or are owned by the user
        if (obj.bit_value.is_shareable and obj.bit_value.is_validated) or owner:
          rest_object = self.convert_object(obj, owner, full, with_definition)
          rest_event.objects.append(rest_object)
    rest_event.comments = list()
    if event.bit_value.is_shareable:
      rest_event.share = 1
    else:
      rest_event.share = 0
    return rest_event

  def convert_object(self, obj, owner, full, with_definition):
    """Converts Object to RestObject"""
    self._get_logger().debug('Converting object')
    rest_object = RestObject()
    rest_object.parent_object_id = obj.parent_object_id
    rest_object.parent_event_id = obj.parent_event_id
    rest_object.definition = self.__convert_obj_def(obj.definition, False, with_definition)
    rest_object.attributes = list()
    if full:
      for attribute in obj.attributes:
        if (attribute.bit_value.is_shareable and attribute.bit_value.is_validated) or owner:
          rest_attribute = self.convert_attribute(attribute, owner, full, with_definition)
          rest_object.attributes.append(rest_attribute)
    rest_object.children = list()
    if full:
      for child in obj.children:
        if (child.bit_value.is_shareable and child.bit_value.is_validated) or owner:
          rest_child_object = self.convert_object(child, owner, full, with_definition)
          rest_object.children.append(rest_child_object)
    if obj.bit_value.is_shareable:
      rest_object.share = 1
    else:
      rest_object.share = 0
    rest_object.author = obj.creator.default_group.name
    return rest_object

  def __convert_obj_def(self, definition, full, with_definition):
    """Converts ObjectDefintion  to RestObjectDefintion"""
    self._get_logger().debug('Converting object definition')
    rest_object_definition = RestObjectDefinition()
    rest_object_definition.chksum = definition.chksum
    if with_definition:
      rest_object_definition.name = definition.name
      rest_object_definition.description = definition.description
      rest_object_definition.attributes = list()
    if full:
      for attribute in definition.attributes:
        # note just 1 level else there is the possibility to make cycles
        rest_attribute_definition = self.__convert_attr_def(attribute, full, with_definition)
        rest_object_definition.attributes.append(rest_attribute_definition)
    rest_object_definition.chksum = definition.chksum
    return rest_object_definition

  def __convert_attr_def(self, definition, full, with_definition):
    """Converts AttribtueDefinition to RestAttributeDefinition"""
    self._get_logger().debug('Converting attribute definition')
    rest_attr_definition = RestAttributeDefinition()
    rest_attr_definition.chksum = definition.chksum

    if with_definition:
      rest_attr_definition.description = definition.description
      rest_attr_definition.name = definition.name
      rest_attr_definition.regex = definition.regex
      rest_attr_definition.class_index = definition.class_index
      rest_attr_definition.handler_uuid = definition.attribute_handler.uuid
      rest_attr_definition.share = definition.share
      rest_attr_definition.relation = definition.relation

    if full:
      # TODO: Find out if this is nessesary
      pass

    rest_attr_definition.chksum = definition.chksum

    return rest_attr_definition

  def convert_attribute(self, attribute, owner, full, with_definition):
    """Converts Attribute to RestAttribtue"""
    rest_attribute = RestAttribute()
    rest_attribute.definition = self.__convert_attr_def(attribute.definition, False, with_definition)
    # determine how to rest value
    try:
      handler = attribute.definition.handler
      value = handler.convert_to_rest_value(attribute, self.__config)
      rest_attribute.value = value
    except HandlerException as error:
      raise DBConversionException(error)
    rest_attribute.ioc = attribute.ioc
    if attribute.bit_value.is_shareable:
      rest_attribute.share = 1
    else:
      rest_attribute.share = 0

    rest_attribute.author = attribute.creator.default_group.name

    if owner:
      # TODO: check If owner is really needed
      pass
    return rest_attribute

  def convert_instance(self, instance, owner, full, with_definition):
    """Converts a DB class to a RestClass"""
    self._get_logger().debug('Starting dictionary conversion')
    # find the rest class name
    if isinstance(instance, Event):
      rest_object = self.convert_event(instance, owner, full, with_definition)

    if isinstance(instance, Object):
      rest_object = self.convert_object(instance, owner, full, with_definition)

    if isinstance(instance, Attribute):
      rest_object = self.convert_attribute(instance, owner, full, with_definition)

    if isinstance(instance, ObjectDefinition):
      rest_object = self.__convert_obj_def(instance, full, with_definition)

    if isinstance(instance, AttributeDefinition):
      rest_object = self.__convert_attr_def(instance, full, with_definition)
    return rest_object

  def __convert_rest_attribute(self, obj, rest_attribute, user, action):
    self._get_logger().debug('Starting conversion of rest object')
    try:
      attribute, additional_attributes = self.attribtue_controller.populate_rest_attributes(user, obj, rest_attribute, action)
      return attribute, additional_attributes
    except ControllerException as error:
      self._get_logger().error(error)
      raise DBConversionException(error)

  def __gen_attr_hash(self, attribute):
    self._get_logger().debug('Generate attribute hasht')
    return hashMD5(attribute.definition.chksum, attribute.plain_value)

  def __convert_rest_object(self, event, parent_object, rest_obj, user, action):
    self._get_logger().debug('Starting conversion of rest object')
    try:
      obj = self.object_controller.populate_rest_object(event,
                                                        rest_obj,
                                                        parent_object,
                                                        user,
                                                        action)

      seen_attributes = list()
      # append attribtues
      if rest_obj.attributes:
        for rest_attribute in rest_obj.attributes:
          attribute, additional_attributes = self.__convert_rest_attribute(obj, rest_attribute, user, action)
          # check if attribute was not already seen and append it
          hash_value = self.__gen_attr_hash(attribute)
          if not hash_value in seen_attributes:
            seen_attributes.append(hash_value)
            obj.attributes.append(attribute)
          if additional_attributes:
            for additional_attribute in additional_attributes:
              hash_value = self.__gen_attr_hash(additional_attribute)
              if not hash_value in seen_attributes:
                seen_attributes.append(hash_value)
                obj.attributes.append(additional_attribute)

      if rest_obj.children:
        for rest_obj_child in rest_obj.children:
          # TODO: find a better way to set the parent_id
          child = self.__convert_rest_object(event,
                                             obj,
                                             rest_obj_child,
                                             user,
                                             action)
          child.parent_event_id = None
          obj.children.append(child)

      return obj
    except ControllerException as error:
      self._get_logger().error(error)
      raise DBConversionException(error)

  def __convert_rest_event(self, rest_event, user, action):
    try:
      if action == 'insert':
        self._get_logger().debug('Starting rest event conversion')
        event = self.event_controller.populate_rest_event(user, rest_event, action)

        if rest_event.objects:
          for rest_obj in rest_event.objects:
            obj = self.__convert_rest_object(event, None, rest_obj, user, action)
            event.objects.append(obj)
        return event
      else:
        raise DBConversionException('Rest supports only inserts')
    except ControllerException as error:
      raise DBConversionException(error)

  def __convert_rest_attr_def(self, rest_attr_def, user, action):
    try:
      attr_def = self.attribtue_controller.populate_rest_attr_def(user, rest_attr_def, action)
      return attr_def
    except ControllerException as error:
      raise DBConversionException(error)

  def __convert_rest_obj_def(self, rest_obj_def, user, action):
    try:
      obj_def = self.object_controller.populate_rest_obj_def(user, rest_obj_def, action)
      for attribute in rest_obj_def.attributes:
        obj_def.attributes.append(self.__convert_rest_attr_def(attribute, user, action))
      return obj_def
    except ControllerException as error:
      raise DBConversionException(error)

  def convert_rest_instance(self, rest_instance, user, action):
    """convert RestObjects back to Objects"""
    self._get_logger().debug('Starting rest conversion')
    # find the rest class name
    if isinstance(rest_instance, RestEvent):
      rest_object = self.__convert_rest_event(rest_instance, user, action)
    elif isinstance(rest_instance, RestAttributeDefinition):
      rest_object = self.__convert_rest_attr_def(rest_instance, user, action)
    elif isinstance(rest_instance, RestObjectDefinition):
      rest_object = self.__convert_rest_obj_def(rest_instance, user, action)
    if not rest_object:
      raise DBConversionException('Rest supports conversion failed')
    return rest_object
