# -*- coding: utf-8 -*-

"""
module providing support for the base handler

Created: Aug, 2013
"""

from abc import ABCMeta, abstractmethod
from ce1sus.helpers.common import strings
from ce1sus.helpers.common.config import Configuration, ConfigSectionNotFoundException
from ce1sus.helpers.common.objects import get_class
from os.path import dirname, abspath
import uuid

from ce1sus.common.system import get_set_group
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.cstix.common.structured_text import StructuredText
from ce1sus.db.classes.internal.common import Properties
from ce1sus.db.classes.internal.path import Path


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class HandlerException(Exception):
  """
  Exception base for handler exceptions
  """
  pass

class HandlerNotFoundException(Exception):
  """
  Exception base for handler exceptions
  """
  pass


class UndefinedException(HandlerException):
  pass


class HandlerBase(object):
  """
  Base class for handlers

  Note this class is abstract
  """
  __metaclass__ = ABCMeta

  def __init__(self):
        # initalize the configuration for the handle and only the for the handlers
    try:
      basePath = dirname(abspath(__file__))
      config = Configuration(basePath + '/../../config/handlers.conf')
    except ConfigSectionNotFoundException as error:
      raise HandlerException(error)
    self.__config = config
    self.is_multi_line = False
    self.cache_object = None
    self.group_broker = None
    self.path_controller = None

  def get_set_group(self, json, cache_object, return_none=False):
    return get_set_group(self.group_broker, json, cache_object, return_none)

  def get_config_value(self, key, default_value=None):
    return self.__config.get(self.__class__.__name__, key.lower(), default_value)

  @staticmethod
  @abstractmethod
  def get_uuid():
    raise HandlerException('get_uuid not defined')

  @staticmethod
  @abstractmethod
  def get_allowed_types():
    raise HandlerException('get_allowed_types not defined')

  @staticmethod
  @abstractmethod
  def get_description():
    raise HandlerException('get_description not defined')

  @abstractmethod
  def assemble(self, obj, json):
    """
    Process of the post over the RestAPI

    :param obj: parent object
    :type obj: Object
    :param definitions: The reqiried definitions
    :type definitions: List of attribute Definitions
    :param user: The user calling the function
    :type user: User
    :param rest_attribute: Attribute inserting over rest
    :type rest_attribute: ReatAttribue

    :returns: Attribute, [List of Attribute], [related_objects]
    """
    raise HandlerException(('insert is not defined for {0} with parameters '
                           + '{1},{2},{3}').format(self.__class__.__name__,
                                                       obj,
                                                       json))

  def get_data(self, instance, parameters):
    raise list()

  @staticmethod
  @abstractmethod
  def get_view_type():
    raise HandlerException('get_view_type is not defined')

  def set_base(self, instance, json, parent, change_base_element=True):
    
    instance.path = Path()
    if json:
      # do not overwrite the uuid
      proposed_uuid = json.get('identifier', None)
      if instance.uuid is None and proposed_uuid:
        instance.uuid = proposed_uuid

    if json and change_base_element:
      # populate properties
      instance.properties.is_validated = json.get('validated', False)
      instance.properties.is_shareable = json.get('shared', False)
      self.cache_object.permission_controller.set_properties_according_to_permisssions(instance, self.cache_object)

      # populate tlp
      tlp = json.get('tlp', None)
      if tlp:
        instance.tlp = tlp.title()
      else:
        instance.tlp = parent.tlp
    else:
      instance.properties = Properties('0', instance)

      self.cache_object.permission_controller.set_properties_according_to_permisssions(instance, self.cache_object)

      if parent:
        instance.tlp = parent.tlp
      else:
        instance.tlp = 'Amber'

    if self.cache_object.insert:
      if json:
        # the creator group is always the group of the user, this is to enable that the group has access to these events
        # even when the user got his group changed or revoked.
        # However this can be set from externally as i.e. inserts from misp or stix uploads
        creat_grp = json.get('creator_group', None)
        if creat_grp:
          instance.creator_group = self.get_set_group(creat_grp, self.cache_object)
        else:
          instance.creator_group = self.cache_object.user.group
      else:
        instance.creator_group = self.cache_object.user.group
        

    if json:
      if self.cache_object.insert:
        # the creator is always the user who inserted it into the DB
        instance.creator = self.cache_object.user

        created_at = json.get('created_at', None)
        if created_at:
          instance.created_at = strings.stringToDateTime(created_at)
        else:
          instance.created_at = self.cache_object.created_at

      # the modifier is always the user who inserted it into the DB
      instance.modifier = self.cache_object.user

      modified_on = json.get('modified_on', None)
      if modified_on:
        instance.modified_on = strings.stringToDateTime(modified_on)
      else:
        instance.modified_on = self.cache_object.created_at

    if instance.uuid is None:
      instance.uuid = '{0}'.format(uuid.uuid4())

    path_instance = self.path_controller.make_path(instance, parent=parent)
    instance.path.event = path_instance.event
    instance.path.path = path_instance.path
    instance.path.dbcode = path_instance.dbcode
    instance.path.tlp_level_id = path_instance.tlp_level_id

  def to_dict(self):
    return {'name': self.__class__.__name__,
            'view_type': self.get_view_type(),
            'is_multi_line': self.is_multi_line
            }

  @staticmethod
  @abstractmethod
  def require_js():
    raise HandlerException('require_js is not defined')

  def get_classname(self):
    return self.__class__.__name__

  def _get_main_definition(self, uuids, definitions):
    """
    Returns the definition using this handler
    """
    diff = list(set(definitions.keys()) - set(uuids))
    if len(diff) == 1:
      main_definition = definitions.get(diff[0], None)
      if main_definition:
        return main_definition
      else:
        raise HandlerException((u'Error determining main definition for {0}').format(self.__class__.__name__))
    else:
      raise HandlerException((u'Could not determine main definition for {0}').format(self.__class__.__name__))

  def _get_definition(self, json, definitions, type_):
    uuid = json.get('definition_id', None)
    if not uuid:
      definition = json.get('definition', None)
      if definition:
        uuid = definition.get('identifier', None)
    if uuid:
      return_definition = definitions.get(uuid)
      if return_definition:
        return return_definition
      raise HandlerException('Could not find a {2} definition with uuid {0} in handler {1}'.format(uuid, self.get_classname(), type_))
    raise HandlerException('Could not find a {2} definition uuid for  generation in handler {1}'.format(uuid, self.get_classname(), type_))

  def _set_definition(self, json, identifier, definitions, type_):
    json['definition_id'] = identifier
    definition = self._get_definition(json, definitions, type_)
    if not definition:
      raise HandlerException('Could not find a {2} definition for uuid {0} generation in handler {1}'.format(identifier, self.get_classname(), type_))

class AttributeHandlerBase(HandlerBase):

  __metaclass__ = ABCMeta

  def __init__(self):
    super(AttributeHandlerBase, self).__init__()
    self.attribute_definitions = dict()
    self.object_definitions = dict()
    self.conditions = dict()

  @staticmethod
  @abstractmethod
  def get_additinal_attribute_uuids():
    """
    Returns a list of additional attributes checksums required for the handling
    """
    return list()

  @staticmethod
  @abstractmethod
  def get_additional_object_uuids(self):
    return list()

  def get_attribute_definition(self, json):
    return self._get_definition(json, self.attribute_definitions, 'attribute')

  def get_object_definition(self, json):
    return self._get_definition(json, self.object_definitions, 'object')

  def set_attribute_definition(self, json, identifier):
    self._set_definition(json, identifier, self.attribute_definitions, 'attribute')

  def set_object_definition(self, json, identifier):
    self._set_definition(json, identifier, self.object_definitions, 'object')

  def get_condition_by_uuid(self, uuid):
    for condition in self.conditions:
      if condition.uuid == uuid:
        return condition
    raise HandlerException(u'Condition with uuid {0} cannot be found'.format(uuid))

  def get_main_definition(self):
    return self._get_main_definition(self.get_additinal_attribute_uuids(), self.attribute_definitions)


  def create_attribute(self, obj, json, change_base_element=True):
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

    attribute = get_class('ce1sus.db.classes.internal.attributes.attribute', 'Attribute')()
    self.set_base(attribute, json, obj, change_base_element)

    # Note first the definition has to be specified else the value cannot be assigned

    definition = self.get_attribute_definition(json)
    attribute.definition = definition

    # Note second the object has to be specified
    attribute.object = obj
    # attribute.object_id = obj.identifier

    # set definition id

    condition_uuid = json.get('condition_id', None)
    # set condition id
    if condition_uuid:
      condition = self.get_condition_by_uuid(condition_uuid)
      attribute.condition = condition
      attribute.condition_id = condition.identifier

    attribute.is_ioc = json.get('ioc', 0)
    attribute.value = json.get('value', None)

    return attribute

  def create_object(self, observable, json, change_base_element=True):
    # TODO recreate object to new setup
    obj = get_class('ce1sus.db.classes.internal.object', 'Object')()
    self.set_base(obj, json, observable, change_base_element)

    definition = self.get_object_definition(json)
    obj.definition = definition

    obj.observable = observable
    return obj



  def create_observable(self, parent, json, change_base_element=True):
    observable = Observable()
    self.set_base(observable, json, parent, change_base_element)

    # set parent
    observable.parent = parent

    observable.description = StructuredText()
    self.set_base(observable.description, json, observable, change_base_element)
    observable.description.value = 'Auto generated'

    return observable


class ReferenceHandlerBase(HandlerBase):

  __metaclass__ = ABCMeta

  def __init__(self):
    super(ReferenceHandlerBase, self).__init__()
    self.reference_definitions = dict()

  @staticmethod
  @abstractmethod
  def get_additinal_reference_uuids():
    return list()

  def get_reference_definition(self, json):
    return self._get_definition(json, self.reference_definitions, 'reference')

  def set_reference_definition(self, json, identifier):
    self._set_definition(json, identifier, self.reference_definitions, 'reference')

  def create_reference(self, report, json, change_base_element=True):
    reference = get_class('ce1sus.db.classes.internal.report', 'Reference')()
    self.set_base(reference, json, report, change_base_element)
    # Note first the definition has to be specified else the value cannot be assigned
    definition = self.get_reference_definition(json)
    reference.definition = definition

    # Note second the object has to be specified
    # reference.report = report

    # set remaining stuff
    reference.value = json.get('value', None)

    return reference

  def get_main_definition(self):
    return self._get_main_definition(self.get_additinal_reference_uuids(), self.reference_definitions)
