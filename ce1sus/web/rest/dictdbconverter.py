# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 25, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
from dagr.helpers.debug import Log
from datetime import datetime
from dagr.controllers.base import ControllerException
from ce1sus.controllers.event.event import EventController
from ce1sus.controllers.event.objects import ObjectsController
from ce1sus.controllers.event.attributes import AttributesController
from dagr.helpers.hash import hashMD5
from ce1sus.api.restclasses import RestEvent, RestObject, RestAttribute, RestObjectDefinition, RestAttributeDefinition, RestGroup
from ce1sus.brokers.event.eventclasses import Event, Object, Attribute
from ce1sus.brokers.definition.definitionclasses import ObjectDefinition, AttributeDefinition
from ce1sus.common.handlers.base import HandlerException
from ce1sus.brokers.permission.permissionclasses import Group
import uuid
from ce1sus.controllers.admin.groups import GroupController
from ce1sus.controllers.event.groups import GroupsController


class DictDBConversionException(Exception):
  """Base exception for this class"""
  pass


class DictDBConverter(object):

  def __init__(self, config):
    self.__config = config
    self.logger = Log(config)
    self.event_controller = EventController(config)
    self.object_controller = ObjectsController(config)
    self.attribtue_controller = AttributesController(config)
    self.group_controller = GroupController(config)
    self.groups_controller = GroupsController(config)

  def _get_logger(self):
    """Returns the class logger"""
    return self.logger.get_logger(self.__class__.__name__)

  def __get_classname(self, restclassname):
    classname = restclassname.replace('Rest', '')
    self._get_logger().debug(u'Found classname {0}'.format(classname))
    return classname

  def convert_to_db_object(self, user, dictionary, action):
    """Maps a dictionary to an instance"""
    self._get_logger().debug(u'Mapping dictionary')
    instance = self.__map_dict_to_object(user, dictionary, action)
    return instance

  def __get_object_data(self, dictionary):
    """ Returns the classname and the corresponding data"""
    self._get_logger().debug(u'Decapsulating dictionary to classname and data')
    if len(dictionary) == 1:
      for key, value in dictionary.iteritems():
        self._get_logger().debug(u'Found class name {0}'.format(key))
        return key, value
    else:
      raise DictDBConversionException(u'Dictionary is malformed expected one entry got more.')

  def __map_dict_to_object(self, user, dictionary, action):
    """ maps dictionary to instances"""
    self._get_logger().debug(u'Start mapping dictionary to object')
    start_time = datetime.now()
    if dictionary:
      restclassname, contents = self.__get_object_data(dictionary)
      classname = self.__get_classname(restclassname)
      if classname == 'Event':
        result = self.__convert_dict_event(user, contents, action)
      elif classname == 'AttributeDefinition':
        result = self.__convert_dict_attribute_definition(user, contents, action)
      elif classname == 'ObjectDefinition':
        result = self.__convert_dict_obejct_definition(user, contents, action)
      else:
        raise DictDBConversionException(u'Class {0} is not supported'.format(classname))
    else:
      result = None
    self._get_logger().debug(u'End mapping dictionary to object. Time elapsed {0}'.format(datetime.now() - start_time))
    return result

  def __convert_dict_attribute_definition(self, user, contents, action):
    if action == 'insert':
      try:
        attr_def = self.attribtue_controller.populate_rest_attr_def(user, contents, action)
        return attr_def
      except ControllerException as error:
        raise DictDBConversionException(error)
    else:
      raise DictDBConversionException('Only insert is supported')

  def __convert_dict_obejct_definition(self, user, contents, action):
    if action == 'insert':
      try:
        obj_def = self.object_controller.populate_rest_obj_def(user, contents, action)
        for attribute_dict in contents.get('attributes', list()):
          attribute = attribute_dict.get('RestAttributeDefinition', None)
          if attribute:
            obj_def.attributes.append(self.__convert_dict_attribute_definition(user, attribute, action))
        return obj_def
      except ControllerException as error:
        raise DictDBConversionException(error)
    else:
      raise DictDBConversionException('Only insert is supported')

  def __convert_dict_to_group(self, user, contents):
    # check if you can set groups
    if user.rights.set_group:
      # check if group exists else create it
      restclassname, contents = self.__get_object_data(contents)
      if restclassname != u'RestGroup':
        raise DictDBConversionException(u'Expected RestGroup but got {0}'.format(restclassname))
      group_name = contents.get('name', None)
      group_uuid = contents.get('uuid', None)
      # TODO: Check if uuid is valid
      group = None
      try:
        # check if string is a correct uuid
        if group_uuid:
          try:
            group = self.groups_controller.get_group_by_uuid(group_uuid)
          except ControllerException:
            if group_name:
              group = self.groups_controller.get_group_by_name(group_name)
      except ControllerException:
        pass

      if not group:
        self._get_logger().debug(u'Group {0} not found creating it'.format(group_name))
        # Create group in db
        group = Group()
        group.name = group_name
        if group_uuid:
          group.uuid = group_uuid
        else:
          group_uuid = uuid.uuid4()
        group.description = u'This group was generated automatically as it was not existing.'
        group.email = None
        group.gpg_key = None
        group.subgroups = list()
        group.users = list()
        group.can_download = 0
        # send mails to users as email of group is not set
        group.usermails = 1
        # Auto create groups are always white
        group.tlp_lvl = 3
        group = self.group_controller.insert_group(group)[1]

      return group
    else:
      return None

  def __convert_dict_event(self, user, contents, action):
    try:
      attr_defs = dict()
      obj_defs = dict()
      if action == 'insert':
        self._get_logger().debug('Starting event conversion')
        # getting event group
        group = self.__convert_dict_to_group(user, contents.get('group', None))
        event = self.event_controller.populate_rest_event(user, group, contents, action)
        objects_dictlist = contents.get('objects', list())
        event.objects = list()
        if objects_dictlist:
          for dictionary in objects_dictlist:
            restclassname, dict_obj = self.__get_object_data(dictionary)
            self._get_logger().debug(u'Starting event conversion converting {0}'.format(restclassname))
            obj = self.__convert_dict_object(user, event, None, dict_obj, action, obj_defs, attr_defs)
            event.objects.append(obj)
        return event
      else:
        raise DictDBConversionException(u'Converter only supports insert')
    except ControllerException as error:
      raise DictDBConversionException(error)

  def __gen_attr_hash(self, attribute):
    hash_str = u'{0}{1}'.format(attribute.definition.chksum, attribute.plain_value)
    self._get_logger().debug(u'Generate attribute hash for {0}'.format(hash_str))
    return hashMD5(hash_str)

  def __convert_dict_object(self, user, event, parent_object, contents, action, obj_defs, attr_defs):
    self._get_logger().debug('Starting conversion of object')
    try:

      group = self.__convert_dict_to_group(user, contents.get('group', None))

      obj = self.object_controller.populate_rest_object(event,
                                                        contents,
                                                        parent_object,
                                                        user,
                                                        group,
                                                        action,
                                                        obj_defs)
      seen_attributes = list()
      # append attribtues
      attribtues_dict = contents.get('attributes', list())
      if attribtues_dict:
        for dictionary in attribtues_dict:
          # create attribute params
          restclassname, attribute_dict = self.__get_object_data(dictionary)
          self._get_logger().debug(u'Starting event conversion converting {0}'.format(restclassname))
          attribute, additional_attributes = self.__convert_dict_attribute(obj, attribute_dict, user, action, attr_defs)
          # check if attribute was not already seen and append it
          hash_value = self.__gen_attr_hash(attribute)
          if hash_value not in seen_attributes:
            seen_attributes.append(hash_value)
            obj.attributes.append(attribute)
          if additional_attributes:
            for additional_attribute in additional_attributes:
              hash_value = self.__gen_attr_hash(additional_attribute)
              if hash_value not in seen_attributes:
                seen_attributes.append(hash_value)
                # attach to parent
                attribute.children.append(additional_attribute)
                obj.attributes.append(additional_attribute)

      children_dict = contents.get('children', list())
      if children_dict:
        for child_dict in children_dict:
          restclassname, cild_contents = self.__get_object_data(child_dict)
          # TODO: find a better way to set the parent_id
          child = self.__convert_dict_object(user,
                                             event,
                                             obj,
                                             cild_contents,
                                             action,
                                             obj_defs,
                                             attr_defs)
          # child.parent_event_id = None
          # TODO: make it better
          obj.children.append(child)
      return obj
    except ControllerException as error:
      self._get_logger().error(error)
      raise DictDBConversionException(error)

  def __convert_dict_attribute(self, obj, dictionary, user, action, attr_defs):
    self._get_logger().debug('Starting conversion of object')
    try:
      group = self.__convert_dict_to_group(user, dictionary.get('group', None))
      attribute, additional_attributes = self.attribtue_controller.populate_rest_attributes(user, group, obj, dictionary, action, attr_defs)
      return attribute, additional_attributes
    except ControllerException as error:
      self._get_logger().error(error)
      raise DictDBConversionException(error)

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

  def __convert_group(self, group):
    rest_group = RestGroup()
    rest_group.name = group.name
    rest_group.uuid = group.uuid
    return rest_group

  def convert_attribute(self, attribute, owner, full, with_definition):
    """Converts Attribute to RestAttribtue"""
    rest_attribute = RestAttribute()
    rest_attribute.definition = self.__convert_attr_def(attribute.definition, False, with_definition)
    rest_attribute.group = self.__convert_group(attribute.creator.default_group)
    rest_attribute.created = attribute.created
    rest_attribute.modified = attribute.modified
    # determine how to rest value
    try:
      handler = attribute.definition.handler
      value = handler.convert_to_rest_value(attribute)
      rest_attribute.value = value
    except HandlerException as error:
      raise DictDBConversionException(error)
    rest_attribute.ioc = attribute.ioc
    if attribute.bit_value.is_shareable:
      rest_attribute.share = 1
    else:
      rest_attribute.share = 0
    rest_attribute.uuid = attribute.uuid
    return rest_attribute

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
    rest_event.group = self.__convert_group(event.creator_group)
    rest_event.created = event.created
    rest_event.modified = event.modified

    rest_event.objects = list()
    if full:
      for obj in event.objects:
        # share only the objects which are shareable or are owned by the user
        if (obj.bit_value.is_shareable and obj.bit_value.is_validated) or owner:
          rest_object = self.convert_object(obj, owner, full, with_definition)
          if rest_object.attributes:
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
    rest_object.event_id = obj.event_id
    rest_object.definition = self.__convert_obj_def(obj.definition, False, with_definition)
    rest_object.group = self.__convert_group(obj.creator.default_group)
    rest_object.created = obj.created
    rest_object.modified = obj.modified
    rest_object.attributes = list()
    rest_object.uuid = obj.uuid
    if obj.parent_object:
      rest_object.parent = obj.parent_object.uuid
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
