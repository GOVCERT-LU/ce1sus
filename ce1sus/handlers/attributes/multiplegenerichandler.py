# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Sep 19, 2013
"""
import types

from ce1sus.db.classes.internal.object import RelatedObject
from ce1sus.handlers.attributes.generichandler import GenericHandler
from ce1sus.handlers.base import HandlerException
from ce1sus.common.classes.cacheobject import CacheObject


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class MultipleGenericHandler(GenericHandler):

  def __init__(self):
    super(GenericHandler, self).__init__()
    self.is_multi_line = True

  @staticmethod
  def get_uuid():
    return '08645c00-8dec-11e3-baa8-0800200c9a66'

  @staticmethod
  def get_description():
    return u'Multiple Generic Handler, usable for a multi-line entries'

  def assemble(self, obj, json):
    self.object_definitions[obj.definition.chksum] = obj.definition
    attr_def_chksum = self.get_main_definition().chksum
    value = json.get('value', None)
    if value:
      if isinstance(value, types.StringTypes):
        values = self.__get_string_attribtues(value)
      else:
        values = value

      if len(values) == 1:
        value = values[0].strip('\n\r')
        json['value'] = value
        attribute = self.create_attribute(obj, json)
        return [attribute], None
      else:
        observables = list()
        related_objects = list()
        # check if create related objects or observables
        create_observables = not obj.related_object_parent

        # the first value belongs always to the existing object
        value = values.pop(0).strip('\n\r')
        json['value'] = value
        attribute = self.create_attribute(obj, json)
        obj.attributes.append(attribute)

        for value in values:
          value = value.strip('\n\r')
          json['value'] = value

          cache_object = CacheObject()
          cache_object.set_default()

          if create_observables:
            observable = self.create_observable(obj, json)
            self.set_object_definition(json, obj.definition.chksum)
            sub_obj = self.create_object(observable, json)
            observable.object = sub_obj
            self.set_attribute_definition(json, attr_def_chksum)
            attribute = self.create_attribute(sub_obj, json)
            sub_obj.attributes.append(attribute)
            observables.append(observable)
          else:
            # create related objects
            self.set_object_definition(json, obj.definition.chksum)
            sub_obj = self.create_object(observable, json)
            self.set_attribute_definition(json, attr_def_chksum)
            attribute = self.create_attribute(sub_obj, json)
            sub_obj.attributes.append(attribute)
            rel_obj = RelatedObject()
            rel_obj.parent_id = obj.related_object_parent[0].parent.identifier
            rel_obj.object = sub_obj
            related_objects.append(rel_obj)

        if observables:
          return observables
        else:
          return related_objects
    else:
      raise HandlerException('No value found for handler {0}'.format(self.__class__.__name__))

  def __get_string_attribtues(self, value):
    return value.split('\n')

  @staticmethod
  def get_view_type():
    return 'multiline'
