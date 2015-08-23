# -*- coding: utf-8 -*-

"""
module handing the generic handler

Created: Sep 19, 2013
"""
import types

from ce1sus.db.classes.ccybox.core.observables import ObservableComposition
from ce1sus.handlers.attributes.generichandler import GenericHandler


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
        
        observable = obj.observable

        # create a composition
        comp_obs = ObservableComposition()
        self.set_base(comp_obs, json, observable)
        comp_obs.parent = observable
        observable.observable_composition = comp_obs

        # move object of the initial observable
        # create containers
        obs = self.create_observable(comp_obs, json)
        obs.object = observable.object
        # detach object from observable
        observable.object = None
        comp_obs.observables.append(obs)

        for value in values:
          value = value.strip('\n\r')
          json['value'] = value

          child_obs = self.create_observable(comp_obs, json)
          child_obs.title = 'second'

          self.set_base(child_obs, json, observable)

          # create object
          self.set_object_definition(json, object_definition_uuid)
          new_obj = self.create_object(child_obs, json)
          # new_obj.parent = child_obs
          self.set_attribute_definition(json, attribute_definition_uuid)

          # append object to observable
          child_obs.object = new_obj

          # create attributes
          attribute = self.create_attribute(new_obj, json)
          new_obj.attributes.append(attribute)

          comp_obs.observables.append(child_obs)

        setattr(observable, 'dontchange', True)
        return [observable]

  def __get_string_attribtues(self, value):
    return value.split('\n')

  @staticmethod
  def get_view_type():
    return 'multiline'
