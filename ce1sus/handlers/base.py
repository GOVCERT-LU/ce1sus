# -*- coding: utf-8 -*-

"""
module providing support for the base handler

Created: Aug, 2013
"""

from ce1sus.helpers.common.config import Configuration, ConfigSectionNotFoundException
from ce1sus.helpers.common.objects import get_class
from datetime import datetime
from os.path import dirname, abspath
from uuid import uuid4

from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.internal.common import Properties


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

  def __init__(self):
        # initalize the configuration for the handle and only the for the handlers
    try:
      basePath = dirname(abspath(__file__))
      config = Configuration(basePath + '/../../config/handlers.conf')
    except ConfigSectionNotFoundException as error:
      raise HandlerException(error)
    self.__config = config
    self.attribute_definitions = dict()
    self.object_definitions = dict()
    self.user = None
    self.conditions = dict()
    self.is_multi_line = False
    self.is_rest_insert = True
    self.is_owner = False
    
  @property
  def reference_definitions(self):
    return self.attribute_definitions

  def get_config_value(self, key, default_value=None):
    return self.__config.get(self.__class__.__name__, key.lower(), default_value)

  @staticmethod
  def get_uuid():
    raise HandlerException('get_uuid not defined')

  @staticmethod
  def get_allowed_types():
    raise HandlerException('get_allowed_types not defined')

  @staticmethod
  def get_description():
    raise HandlerException('get_description not defined')

  def get_additinal_attribute_chksums(self):
    """
    Returns a list of additional attributes checksums required for the handling
    """
    raise HandlerException(('get_additinal_attribute_chksums not defined for {0}').format(self.__class__.__name__))

  def get_additional_object_chksums(self):
    raise HandlerException(('get_additional_object_chksums not defined for {0}').format(self.__class__.__name__))

  def get_additinal_reference_chksums(self):
    raise HandlerException(('get_additinal_reference_chksums not defined for {0}').format(self.__class__.__name__))

  def get_attriute_definition(self, chksum):
    definition = self.attribute_definitions.get(chksum, None)
    if definition:
      return definition
    else:
      raise HandlerException(u'Attribute definition with chksum {0} cannot be found'.format(chksum))

  def get_reference_definition(self, chksum):
    definition = self.reference_definitions.get(chksum, None)
    if definition:
      return definition
    else:
      raise HandlerException(u'Reference definition with chksum {0} cannot be found'.format(chksum))

  def get_condition_by_uuid(self, uuid):
    for condition in self.conditions:
      if condition.uuid == uuid:
        return condition
    raise HandlerException(u'Condition with uuid {0} cannot be found'.format(uuid))

  def get_attriute_definition_by_uuid(self, uuid):
    for value in self.attribute_definitions.itervalues():
      if value.uuid == uuid:
        return value
    raise HandlerException(u'Attribute definition with uuid {0} cannot be found'.format(uuid))

  def get_object_definition_by_uuid(self, uuid):
    for value in self.object_definitions.itervalues():
      if value.uuid == uuid:
        return value
    raise HandlerException(u'Object definition with uuid {0} cannot be found'.format(uuid))

  def get_object_definition(self, chksum):
    definition = self.object_definitions.get(chksum, None)
    if definition:
      return definition
    else:
      raise HandlerException(u'Object definition with chksum {0} cannot be found'.format(chksum))

  def get_main_definition(self):
    """
    Returns the definition using this handler
    """
    chksums = self.get_additinal_attribute_chksums()
    diff = list(set(self.attribute_definitions.keys()) - set(chksums))
    if len(diff) == 1:
      main_definition = self.attribute_definitions.get(diff[0], None)
      if main_definition:
        return main_definition
      else:
        raise HandlerException((u'Error determining main definition for {0}').format(self.__class__.__name__))
    else:
      raise HandlerException((u'Could not determine main definition for {0}').format(self.__class__.__name__))

  def insert(self, obj, user, json):
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
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       obj,
                                                       user,
                                                       json))

  def update(self, attribtue, user, json):
    """
    Process of the post over the RestAPI

    :returns: Attribute
    """
    raise HandlerException(('update is not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       attribtue,
                                                       user,
                                                       json))

  def remove(self, attribtue, user, json):
    raise HandlerException(('remove is not defined for {0} with parameters '
                           + '{1},{2},{3},{4}').format(self.__class__.__name__,
                                                       attribtue,
                                                       user,
                                                       json))

  def set_base(self, instance, json, user, parent):
    instance.properties = Properties('0', instance)

    tlp = json.get('tlp', None)
    if tlp:
      tlp = tlp.title()
    else:
      tlp = parent.tlp
    instance.tlp = tlp

    instance.creator_group_id = user.group.identifier
    instance.creator_group = user.group
    instance.creator_id = user.identifier
    instance.creator = user
    instance.modifier = user
    instance.modifier_id = user.identifier
    instance.created_at = datetime.utcnow()
    instance.modified_on = datetime.utcnow()
    instance.properties.is_rest_instert = self.is_rest_insert
    instance.properties.is_web_insert = not self.is_rest_insert
    shared = json.get('properties', {}).get('shared', False)

    if shared:
      instance.properties.is_shareable = True

    if self.is_owner:
      instance.properties.is_validated = True
    else:
      instance.properties.is_proposal = True



  def create_attribute(self, obj, definition, user, json, set_parent=True):
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
    self.set_base(attribute, json, user, obj)

    # Note first the definition has to be specified else the value cannot be assigned
    attribute.definition = definition

    # Note second the object has to be specified
    attribute.object = obj
    attribute.object_id = obj.identifier

    # set definition id
    attribute.definition = definition
    condition_uuid = json.get('condition_id', None)
    # set condition id
    if condition_uuid:
      condition = self.get_condition_by_uuid(condition_uuid)
      attribute.condition = condition
      attribute.condition_id = condition.identifier

    attribute.is_ioc = json.get('ioc', 0)
    attribute.value = json.get('value', None)
    attribute.tlp = json.get('tlp', 'Amber').title()

    return attribute

  def create_reference(self, report, definition, user, json):
    reference = get_class('ce1sus.db.classes.internal.report', 'Reference')()
    self.set_base(reference, json, user, report)
    # Note first the definition has to be specified else the value cannot be assigned
    reference.definition = definition

    # Note second the object has to be specified
    reference.report = report

    # set remaining stuff
    reference.value = json.get('value', None)

    return reference

  def create_object(self, obsevable, definition, user, json, has_parent_observable=True):
    # TODO recreate object to new setup
    obj = get_class('ce1sus.db.classes.internal.object', 'Object')()
    self.set_base(obj, json, user, obsevable)

    obj.definition = definition

    obj.observable = obsevable

    if has_parent_observable:
      obj.parent = obsevable

    return obj

  def get_data(self, attribute, definition, parameters):
    raise HandlerException(('frontend_get is not defined for {0}').format(self.__class__.__name__))

  def get_view_type(self):
    raise HandlerException(('get_view_type is not defined for {0}').format(self.__class__.__name__))

  def to_dict(self):
    return {'name': self.__class__.__name__,
            'view_type': self.get_view_type(),
            'is_multi_line': self.is_multi_line
            }

  def require_js(self):
    raise HandlerException(u'require_js is not defined for {0}'.format(self.__class__.__name__))

  def get_classname(self):
    return self.__class__.__name__

  def create_observable(self, attribute):
    observable = Observable()
    self.set_base(observable, {}, attribute.creator, attribute)
    # set new uuid for the parent

    event = attribute.object.event
    observable.event = event

    observable.created_at = datetime.utcnow()
    observable.modified_on = datetime.utcnow()
    observable.description = 'Auto generated'
    observable.uuid = uuid4()
    observable.properties = attribute.properties

    return observable
