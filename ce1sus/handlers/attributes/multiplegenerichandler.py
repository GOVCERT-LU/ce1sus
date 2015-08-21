# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Sep 19, 2013
"""
import types

from ce1sus.common.classes.cacheobject import CacheObject
from ce1sus.db.classes.ccybox.core.observables import ObservableComposition
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

  def assemble(self, obj, json):
    self.object_definitions[obj.definition.uuid] = obj.definition
    object_definition_uuid = obj.definition.uuid
    attribute_definition_uuid = json.get('definition_id', None)
    
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
        return [attribute]
      else:
        # the first value belongs always to the existing object
        value = values.pop(0).strip('\n\r')
        json['value'] = value
        attribute = self.create_attribute(obj, json)
        #append the first one
        obj.attributes.append(attribute)
        
        observable = obj.get_observable()
        for value in values:
          value = value.strip('\n\r')
          json['value'] = value

          cache_object = CacheObject()
          cache_object.set_default()
          
          if observable.observable_composition:
            child_obs = self.create_observable(obj, json)
            child_obs.delink_parent()
            self.set_object_definition(json, object_definition_uuid)
            new_obj = self.create_object(observable, json)
            self.set_attribute_definition(json, attribute_definition_uuid)
            attribute = self.create_attribute(obj, json)
            new_obj.attributes.append(attribute)
            child_obs.object = new_obj
            observable.observable_composition.append(child_obs)
          else:
            #create a composition
            comp_obs = ObservableComposition()
            self.set_base(comp_obs, json, observable)
            comp_obs.observable = observable
            observable.observable_composition = comp_obs

            # create containers
            first_child_obs = self.create_observable(obj, json)
            first_child_obs.delink_parent()
            #append the object to a different observable
            first_child_obs.object = obj
            # detach object from observable
            observable.object = None
            
            second_child_obs = self.create_observable(obj, json)
            second_child_obs.delink_parent()
            self.set_object_definition(json, object_definition_uuid)
            new_obj = self.create_object(observable, json)
            self.set_attribute_definition(json, attribute_definition_uuid)
            attribute = self.create_attribute(obj, json)
            new_obj.attributes.append(attribute)
            
            second_child_obs.object = new_obj
            
            comp_obs.observables.append(first_child_obs)
            comp_obs.observables.append(second_child_obs)

        setattr(observable, 'dontchange', True)
        return [observable]

  def __get_string_attribtues(self, value):
    return value.split('\n')

  @staticmethod
  def get_view_type():
    return 'multiline'
