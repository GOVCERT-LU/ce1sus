# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Sep 19, 2013
"""
import types

from ce1sus.db.classes.internal.object import RelatedObject
from ce1sus.handlers.attributes.generichandler import GenericHandler
from ce1sus.handlers.base import HandlerException


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

  def insert(self, obj, user, json):
    value = json.get('value', None)
    if value:
      definition = self.get_main_definition()
      if isinstance(value, types.StringTypes):
        values = self.__get_string_attribtues(value)
      else:
        values = value

      if len(values) == 1:
        value = values[0].strip('\n\r')
        json['value'] = value
        attribute = self.create_attribute(obj, definition, user, json)
        return [attribute], None
      else:
        observables = list()
        related_objects = list()
        # check if create related objects or observables
        create_observables = not obj.related_object_parent

        for value in values:
          value = value.strip('\n\r')
          json['value'] = value
          attribute = self.create_attribute(obj, definition, user, json, False)

          if create_observables:
            observable = self.create_observable(attribute)
            sub_obj = self.create_object(observable, obj.definition, user, obj.to_dict(), True)
            attribute.object_id = sub_obj.identifier
            attribute.object = sub_obj
            sub_obj.attributes.append(attribute)
            observables.append(observable)
          else:
            # create related objects
            sub_obj = self.create_object(obj.observable, obj.definition, user, obj.to_dict(), False)
            sub_obj.parent = None
            sub_obj.parent_id = None
            attribute.object_id = sub_obj.identifier
            attribute.object = sub_obj
            sub_obj.attributes.append(attribute)
            rel_obj = RelatedObject()
            rel_obj.parent_id = obj.related_object_parent[0].parent.identifier
            rel_obj.object = sub_obj
            related_objects.append(rel_obj)

        if observables:
          return observables, None
        else:
          return None, related_objects

    else:
      raise HandlerException('No value found for handler {0}'.format(self.__class__.__name__))

  def __get_string_attribtues(self, value):
    return value.split('\n')

  def get_view_type(self):
    return 'multiline'
