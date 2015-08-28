# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 5, 2015
"""
from ce1sus.helpers.common import strings
from uuid import uuid4
import uuid

from ce1sus.common.checks import set_properties_according_to_permisssions
from ce1sus.common.system import get_set_group
from ce1sus.controllers.base import BaseController
from ce1sus.db.classes.common.baseelements import Entity
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.cstix.common.identity import Identity
from ce1sus.db.classes.cstix.common.information_source import InformationSource, InformationSourceRole
from ce1sus.db.classes.internal.common import Properties
from ce1sus.db.classes.internal.core import BaseElement, ExtendedLogingInformations, SimpleLoggingInformations, BaseObject
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class BaseChangerException(Exception):
  pass

class UpdaterException(BaseChangerException):
  pass

class MergerException(BaseChangerException):
  pass

class BaseChanger(BaseController):

  def __set_baseobject(self, instance, json):
    # instance.identifier autogenerated by DB
    if json:
      # do not overwrite the uuid
      proposed_uuid = json.get('identifier', None)
      if instance.uuid is None and proposed_uuid:
        instance.uuid = proposed_uuid
    if instance.uuid is None:
      instance.uuid = '{0}'.format(uuid.uuid4())

  def __set_simple_logging(self, instance, json, cache_object):
    self.__set_baseobject(instance, json)
    if json:
      if cache_object.insert:
        # the creator is always the user who inserted it into the DB
        instance.creator = cache_object.user

        created_at = json.get('created_at', None)
        if created_at:
          instance.created_at = strings.stringToDateTime(created_at)
        else:
          instance.created_at = cache_object.created_at

      # the modifier is always the user who inserted it into the DB
      instance.modifier = cache_object.user

      modified_on = json.get('modified_on', None)
      if modified_on:
        instance.modified_on = strings.stringToDateTime(modified_on)
      else:
        instance.modified_on = instance.created_at

    else:
      if cache_object.insert:
        # the creator is always the user who inserted it into the DB
        instance.creator = cache_object.user
        instance.created_at = cache_object.created_at

      instance.modifier = cache_object.user
      instance.modified_on = instance.created_at

  def __set_extended_logging(self, instance, json, cache_object):
    self.__set_simple_logging(instance, json, cache_object)
    if cache_object.insert:
      if json:
        # the creator group is always the group of the user, this is to enable that the group has access to these events
        # even when the user got his group changed or revoked.
        # However this can be set from externally as i.e. inserts from misp or stix uploads
        creat_grp = json.get('creator_group', None)
        if creat_grp:
          instance.creator_group = self.get_set_group(creat_grp, cache_object)
        else:
          instance.creator_group = cache_object.user.group
      else:
        instance.creator_group = cache_object.user.group

  def __set_properties(self, instance, json, cache_object):
    if json:
      instance.properties.is_validated = json.get('validated', False)

      instance.properties.is_shareable = json.get('shared', False)
    # Set it as proposal if the user is not the event owner
    set_properties_according_to_permisssions(instance.properties, cache_object)

  def __set_baseelement(self, instance, json, cache_object, parent, change_base_element=True):
    self.__set_extended_logging(instance, json, cache_object)

    if json and change_base_element:
      # populate properties
      self.__set_properties(instance, json.get('properties', None), cache_object)

      # populate tlp
      tlp = json.get('tlp', None)
      if tlp:
        instance.tlp = tlp.title()
      else:
        instance.tlp = parent.tlp
    else:
      instance.properties = Properties('0', instance)

      set_properties_according_to_permisssions(instance.properties, cache_object)

      if parent:
        instance.tlp = parent.tlp
      else:
        instance.tlp = 'Amber'

  def __set_entity(self, instance, json, cache_object, parent, change_base_element=True):
    self.__set_baseelement(instance, json, cache_object, parent, change_base_element)

  def __set_basecomponent(self, instance, json, cache_object, parent, change_base_element=True):
    self.__set_entity(instance, json, cache_object, parent, change_base_element)

    if json:
      instance.id_ = json.get('id_', None)
      idref = json.get('idref', None)
      if not idref:
        description = json.get('description', None)
        if description:
          description = self.assemble_structured_text(instance, description, cache_object)
          instance.description = description
        short_description = json.get('short_description', None)
        if short_description:
          short_description = self.assemble_structured_text(instance, short_description, cache_object)
          instance.short_description = short_description
      information_source = json.get('information_source', None)
      if information_source:
        information_source = self.assemble_information_source(instance, information_source, cache_object)
        instance.information_source = information_source
      handling = json.get('handling', None)
      if handling:
        handling = self.assemble_handling(instance, handling, cache_object)
        instance.handling = handling

      instance.title = json.get('title', None)
      version = json.get('version', None)
      instance.version = Version(version, instance)

  def get_set_group(self, json, cache_object, return_none=False):
    return get_set_group(self.group_broker, json, cache_object, return_none)

  def set_base(self, instance, json, cache_object, parent, change_base_element=True):
    if isinstance(instance, BaseCoreComponent):
      self.__set_basecomponent(instance, json, cache_object, parent, change_base_element)
    elif isinstance(instance, Entity):
      self.__set_entity(instance, json, cache_object, parent, change_base_element)
    elif isinstance(instance, BaseElement):
      self.__set_baseelement(instance, json, cache_object, parent, change_base_element)
    elif isinstance(instance, ExtendedLogingInformations):
      self.__set_extended_logging(instance, json, cache_object)
    elif isinstance(instance, SimpleLoggingInformations):
      self.__set_simple_logging(instance, json, cache_object)
    elif isinstance(instance, BaseObject):
      self.__set_baseobject(instance, json)

  def create_information_source(self, parent, json, cache_object, role='Initial Author'):
    information_source = InformationSource()
    self.set_base(information_source, json, cache_object, parent)
    information_source.uuid = uuid4()
    isrole = InformationSourceRole()
    isrole.role = role
    self.set_base(isrole, json, cache_object, information_source)
    isrole.uuid = uuid4()
    # TODO: use variable instead
    information_source.roles.append(isrole)
    information_source.identity = Identity()
    self.set_base(information_source.identity, json, cache_object, information_source)
    information_source.identity.uuid = uuid4()
    if not information_source.identity.name:
      information_source.identity.name = cache_object.user.group.name
    return information_source
