# -*- coding: utf-8 -*-

"""
(Description)

Created on 7 Sep 2015
"""
from ce1sus.helpers.common.objects import get_fields

from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.object import Object
from ce1sus.db.classes.internal.path import Path
from ce1sus.db.common.broker import BrokerException, NothingFoundException
import cybox


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# not mappable items as they are present twice in the object
NOT_MAPPED = [
              'File_HashList_md5',
              'File_HashList_sha1',
              'File_HashList_sha256',
              'File_HashList_sha384',
              'File_HashList_sha512'
              ]

#Don't know how to map these yet
NOT_MAPPED_SUFFIXES = [
                       'datatype',
                       'default_datatype',
                       'apply_condition',
                       'is_case_sensitive',
                       'delimiter',
                       ]

# if a special mapping is required
MAPED_ATTRIBUTES = {}


class CyboxConverterException(Exception):
  pass


class CyboxConverter(BaseController):

  def __init__(self, config, session=None):
    super(CyboxConverter, self).__init__(config, session)


  def set_base(self, instance, parent=None):
    instance.path = Path()
    if parent:
      instance.tlp_level_id = parent.tlp_level_id
      instance.dbcode = parent.dbcode
      instance.path.event = parent.path.event
      instance.modified_on = parent.modified_on
      instance.created_on = parent.created_on
      instance.creator_group = parent.creator_group
      instance.creator = parent.creator
      instance.modifier = parent.modifier

  def get_object_definition(self, instance, cache_object):
    try:
      name = instance.properties.__class__.__name__
      definition = cache_object.seen_obj_defs.get(name, None)
      if definition:
        return definition
      else:
        definition = self.obj_def_broker.get_defintion_by_name(name)
        cache_object.seen_obj_defs[name] = definition
        return definition
      return definition
    except NothingFoundException as error:
      raise ControllerException('Object definition "{0}" cannot be found'.format(name))
    except BrokerException as error:
      self.logger.error(error)
      raise ControllerException(error)

  def __sanitize(self, text):
    if text.endswith('_'):
      return text[:-1]
    else:
      return text

  def is_not_mappable(self, identifier):
    if identifier in NOT_MAPPED:
      return True
    else:
      for item in NOT_MAPPED_SUFFIXES:
        if identifier.endswith(item):
          return True
    return False
    

  def get_attribute_definition(self, name, name_prefix, cache_object):
    identifier = '{0}_{1}'.format(name_prefix, name)
    identifier = self.__sanitize(identifier)
    self.logger.debug('Getting attribute definition for {0}'.format(identifier))
    remapped_name = MAPED_ATTRIBUTES.get(identifier, None)
    if self.is_not_mappable(identifier):
      return None
    else:
      if remapped_name is None:
        remapped_name = identifier.split('_', 1)[1]

      try:
        definition = cache_object.seen_attr_defs.get(remapped_name, None)
        if definition:
          return definition
        else:
          definition = self.attr_def_broker.get_defintion_by_name(remapped_name, lower=True)
          cache_object.seen_attr_defs[remapped_name] = definition
          return definition
        return definition
      except NothingFoundException as error:
        try:
          definition = self.attr_def_broker.get_defintion_by_name(identifier, lower=True)
          cache_object.seen_attr_defs[remapped_name] = definition
          return definition
        except NothingFoundException as error:
          raise ControllerException('Attribute Definition "{0}" or "{1}" cannot be found'.format(identifier, remapped_name))
      except BrokerException as error:
        self.logger.error(error)
        raise ControllerException(error)

  def map_attribtues(self, properties, cache_object, parent, name_prefix=None):
    if name_prefix:
      name = '{0}_{1}'.format(name_prefix, properties.__class__.__name__)
    else:
      name = properties.__class__.__name__

    for field in get_fields(properties):
      if not field.isupper():
        value = getattr(properties, field)
        if value:
          if isinstance(value, cybox.common.properties.String):
            definition = self.get_attribute_definition(field, name, cache_object)
            if definition:
              attribute = self.map_attribute(definition, value, parent)
              parent.attributes.append(attribute)
          elif isinstance(value, cybox.Entity):
            self.map_attribtues(value, cache_object, parent, name_prefix=name)
          else:
            definition = self.get_attribute_definition(field, name, cache_object)
            if definition:
              attribute = self.map_attribute(definition, value, parent)
              parent.attributes.append(attribute)

  def map_attribute(self, definition, value, parent):
    attribute = Attribute()
    self.set_base(attribute, parent)
    attribute.object = parent
    attribute.definition = definition
    attribute.value = value
    return attribute

  def map_object(self, instance, cache_object, parent):
    obj = Object()
    self.set_base(obj, parent)
    obj.id_ = instance.id_
    obj.idref = instance.idref
    obj.observable = parent
    if obj.idref is None:
      definition = self.get_object_definition(instance, cache_object)
      obj.definition = definition
      self.map_attribtues(instance.properties, cache_object, obj)
    return obj
