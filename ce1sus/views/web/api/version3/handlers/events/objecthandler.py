# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""

from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.conditions import ConditionController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.attributecontroller import AttributeController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.common import ValueException
from ce1sus.db.classes.internal.object import RelatedObject
from ce1sus.handlers.base import HandlerException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, PathParsingException, RestHandlerException, RestHandlerNotFoundException, require
from ce1sus.controllers.common.merger.merger import Merger


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObjectHandler(RestBaseHandler):

  def __init__(self, config):
    super(ObjectHandler, self).__init__(config)
    self.observable_controller = self.controller_factory(ObservableController)
    self.attribute_controller = self.controller_factory(AttributeController)
    self.attribute_definition_controller = self.controller_factory(AttributeDefinitionController)
    self.object_definition_controller = self.controller_factory(ObjectDefinitionController)
    self.relations_controller = self.controller_factory(RelationController)
    self.conditions_controller = self.controller_factory(ConditionController)
    self.merger = self.controller_factory(Merger)
  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def object(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      cache_object = self.get_cache_object(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      # get the event
      object_id = requested_object.get('event_id')
      if object_id:
        obj = self.observable_controller.get_object_by_uuid(object_id)
        event = obj.event
        self.check_if_event_is_viewable(event)
        self.set_event_properties_cache_object(cache_object, event)

        if requested_object['object_type'] is None:
                    # return the event

                    # check if event is viewable by the current user

          return self.__process_object(method, event, obj, json, cache_object)

        elif requested_object['object_type'] == 'related_object':
          return self.__process_related_object(method, event, obj, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'attribute':
          return self.__process_attribute(method, event, obj, requested_object, json, cache_object)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Object cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_object(self, method, event, obj, json, cache_object):
    try:
      if method == 'POST':
        raise RestHandlerException('Please use observable/{uuid}/instead')
      else:
        if method == 'GET':
          self.check_item_is_viewable(event, obj)
          return obj.to_dict(cache_object)
        elif method == 'PUT':
          old_obj = obj
          self.check_if_event_is_modifiable(event)
          self.check_item_is_viewable(event, obj)
          self.check_if_user_can_set_validate_or_shared(event, old_obj, cache_object.user, json)
          # check if there was not a parent set
          parent_id = json.get('parent_object_id', None)
          # TODO Review the relations as they have to be removed at some point if they were existing
          if parent_id:
                        # get related object
            related_object = self.observable_controller.get_related_object_by_child(obj)
            # check if parent has changed
            if related_object.parent_id != parent_id:
                            # unbind the earlier relation
              related_object.parent_id = parent_id
              related_object.relation = json.get('relation', None)
              self.observable_controller.update_related_object(related_object, cache_object, False)
          self.updater.update(obj, json, cache_object)
          self.observable_controller.update_object(obj, cache_object, True)
          return obj.to_dict(cache_object)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          self.check_item_is_viewable(event, obj)
          self.observable_controller.remove_object(obj, cache_object, True)
          return 'Deleted object'
    except ValueException as error:
      raise RestHandlerException(error)

  def __process_related_object(self, method, event, obj, requested_object, json, cache_object):
    if method == 'POST':

      # workaround
      # TODO find out why the parent gets deleted
      self.check_if_user_can_add(event)
      related_object = self.assembler.assemble(json, RelatedObject, obj, cache_object)
      self.observable_controller.update_object(obj, cache_object, True)
      return related_object.to_dict(cache_object)
    elif method == 'DELETE':
      self.check_if_event_is_modifiable(event)
      self.check_item_is_viewable(event, obj)
      uuid = requested_object['object_uuid']
      if uuid:
        try:
          related_object = self.observable_controller.get_related_object_by_uuid(uuid)
        except ControllerNothingFoundException:
          related_object = self.observable_controller.get_related_object_by_child(obj)

        self.observable_controller.remove_related_object(related_object, cache_object)
        return 'OK'
      else:
        raise RestHandlerException('No uuid given')
      
    else:
      raise RestHandlerException('Method {0} is not available'.format(method))

  def __make_attribute_insert_return(self, param_1, related_objects, is_observable, cache_object):
    result_objects = list()
    if related_objects:
      for related_object in related_objects:
        result_objects.append(related_object.to_dict(cache_object))

    if is_observable and param_1:
      cache_object.infalted = True
      return {'observable': param_1.to_dict(cache_object), 'related_objects': result_objects}
    else:
      result_attriutes = list()

      if param_1:
        for attr in param_1:
          result_attriutes.append(attr.to_dict(cache_object))

      return {'attributes': result_attriutes, 'related_objects': result_objects}

  def __get_attribtues_for_object(self, obj):
    result = obj.attributes
    if obj.related_objects:
      for rel_obj in obj.related_objects:
        result = result + self.__get_attribtues_for_object(rel_obj.object)
    return result

  def __get_attribtues_for_observable(self, obs):
    result = list()
    if obs.object:
      result = result + self.__get_attribtues_for_object(obs.object)
    return result

  def __get_all_attribtues(self, param_1, related_objects, is_observable):
    result = list()
    if is_observable and param_1:
      # then param 1 is an wrapped composed observable
      if param_1.observable_composition:
        for obs in param_1.observable_composition.observables:
          result = result + self.__get_attribtues_for_observable(obs)
      else:
        result = result + self.__get_attribtues_for_observable(param_1)
    else:
      if param_1:
        result = result + param_1
      if related_objects:
        for rel_obj in related_objects:
          result = result + self.__get_attribtues_for_object(rel_obj.object)
    return result

  def __process_attribute(self, method, event, obj, requested_object, json, cache_object):
    try:

      if method == 'POST':
        self.check_if_user_can_add(event)
        cache_object_copy = cache_object.make_copy()
        cache_object_copy.complete = True
        cache_object_copy.inflated = True

        # NOTE: the assembler for attribute assembler returns a number as the object are directly attached to the object
        returnvalues = self.assembler.assemble(json, Attribute, obj, cache_object)
        if isinstance(returnvalues, list):
          self.attribute_controller.insert_attributes(returnvalues, cache_object, True)
          return returnvalues[0].object.to_dict(cache_object_copy)
        else:
          self.observable_controller.update_object(returnvalues, cache_object, True)
          return returnvalues.to_dict(cache_object_copy)
      else:
        uuid = requested_object['object_uuid']
        if method == 'GET':
          if uuid:
            attribute = self.attribute_controller.get_attribute_by_uuid(uuid)
            self.check_item_is_viewable(event, attribute)
            return attribute.to_dict(cache_object)
          else:
            result = list()
            for attribute in obj.attributes:
              if self.is_item_viewable(event, attribute):
                result.append(attribute.to_dict(cache_object))
            return result
        else:
          attribute = self.attribute_controller.get_attribute_by_uuid(uuid)
          if method == 'PUT':
            old_attr = attribute
            self.check_if_event_is_modifiable(event)
            self.check_item_is_viewable(event, attribute)
            self.check_if_user_can_set_validate_or_shared(event, old_attr, cache_object.user, json)
            definition_uuid = json.get('definition_id', None)

            if definition_uuid:
              # check if it still is the same
              if attribute.definition.uuid != definition_uuid:
                raise HandlerException('It is not possible to change the definition of attribtues')

            handler_instance = self.__get_handler(attribute.definition)
            handler_instance.is_rest_insert = cache_object.rest_insert
            handler_instance.is_owner = cache_object.owner

            # Ask handler to process the json for the new attributes
            attribute = handler_instance.update(attribute, cache_object.user, json)

            self.logger.info(u'User {0} changed attribute {1} from {2} to {3}'.format(cache_object.user.username, attribute.identifier, old_attr.value, attribute.value))

            # TODO: check if there are no children attached
            self.attribute_controller.update_attribute(attribute, cache_object, True)

            return attribute.to_dict(cache_object)
          elif method == 'DELETE':
            self.check_if_event_is_deletable(event)
            self.check_item_is_viewable(event, attribute)
            self.attribute_controller.remove_attribute(attribute, cache_object, True)
            return 'Deleted object'

    except ValueException as error:
      raise RestHandlerException(error)
