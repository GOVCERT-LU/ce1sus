# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""

from types import ListType
from uuid import uuid4

from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.conditions import ConditionController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.attributecontroller import AttributeController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.db.classes.internal.attributes.attribute import Attribute
from ce1sus.db.classes.internal.common import ValueException
from ce1sus.db.classes.internal.object import Object, RelatedObject
from ce1sus.db.classes.ccybox.core.observables import ObservableComposition, Observable
from ce1sus.handlers.base import HandlerException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, PathParsingException, RestHandlerException, RestHandlerNotFoundException, require


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
    super(RestBaseHandler, self).__init__(config)
    self.observable_controller = self.controller_factory(ObservableController)
    self.attribute_controller = self.controller_factory(AttributeController)
    self.attribute_definition_controller = self.controller_factory(AttributeDefinitionController)
    self.object_definition_controller = self.controller_factory(ObjectDefinitionController)
    self.relations_controller = self.controller_factory(RelationController)
    self.conditions_controller = self.controller_factory(ConditionController)

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

        elif requested_object['object_type'] == 'object':
          return self.__process_child_object(method, event, obj, requested_object, json, cache_object)
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
              self.observable_controller.update_related_object(related_object, cache_object.user, False)
          obj = self.updater.update(obj, json, cache_object)
          self.observable_controller.update_object(obj, cache_object.user, True)
          return obj.to_dict(cache_object)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          self.check_item_is_viewable(event, obj)
          self.observable_controller.remove_object(obj, cache_object.user, True)
          return 'Deleted object'
    except ValueException as error:
      raise RestHandlerException(error)

  def __process_child_object(self, method, event, obj, requested_object, json, cache_object):
    if method == 'POST':

      # workaround
      # TODO find out why the parent gets deleted
      self.check_if_user_can_add(event)
      related_object = self.assembler.assemble(json, RelatedObject, obj, cache_object)
      self.observable_controller.update_object(obj, cache_object.user, True)
      return related_object.to_dict(cache_object)
    else:
      raise RestHandlerException('Please use object/{uuid}/ instead')

  def __get_handler(self, definition, cache_object):
    handler_instance = definition.handler
    handler_instance.attribute_definitions[definition.chksum] = definition

    # Check if the handler requires additional attribute definitions
    additional_attr_defs_chksums = handler_instance.get_additinal_attribute_chksums()

    if additional_attr_defs_chksums:
      additional_attr_definitions = self.attribute_definition_controller.get_defintion_by_chksums(additional_attr_defs_chksums)
      for additional_attr_definition in additional_attr_definitions:
        handler_instance.attribute_definitions[additional_attr_definition.chksum] = additional_attr_definition

    # Check if the handler requires additional object definitions
    additional_obj_defs_chksums = handler_instance.get_additional_object_chksums()

    if additional_obj_defs_chksums:
      additional_obj_definitions = self.object_definition_controller.get_object_definition_by_chksums(additional_obj_defs_chksums)
      for additional_obj_definition in additional_obj_definitions:
        handler_instance.object_definitions[additional_obj_definition.chksum] = additional_obj_definition

    handler_instance.user = cache_object.user

    # set conditions
    conditions = self.conditions_controller.get_all_conditions()
    handler_instance.conditions = conditions

    return handler_instance

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
        # Get needed handler
        definition = self.attribute_definition_controller.get_attribute_definitions_by_uuid(json.get('definition_id', None))
        handler_instance = self.__get_handler(definition, cache_object)
        # set provenace to handler
        handler_instance.is_rest_insert = cache_object.rest_insert
        handler_instance.is_owner = cache_object.owner
        # Ask handler to process the json for the new attributes/observables
        # param 1 can be either a list of attributes or a list of observables
        param_1, related_objects = handler_instance.insert(obj, cache_object.user, json)

        is_observable = True
        # checks for param 1:
        if isinstance(param_1, ListType):
          if len(param_1) > 0:
            first_element = param_1[0]
            if isinstance(first_element, Attribute):
              is_observable = False
            elif isinstance(first_element, Object):
              is_observable = False
          else:
            raise RestHandlerException('Fist parameter is an empty list for handler {0}'.format(definition.attribute_handler.classname))
        else:
          if not related_objects:
            is_observable = False
            raise RestHandlerException('Fist parameter and related_objects are not a list or are empty for handler {0}'.format(definition.attribute_handler.classname))
        modified_obj = False
        if is_observable and param_1:
          # make a composed observable for the observables gotten an the observable of the originating object
          observable = obj.observable

          # check if there is already a composed observable on top if there is add the observables
          try:
            test_composition = self.observable_controller.get_composition_by_observable(observable)
          except ControllerNothingFoundException:
            test_composition = None

          if test_composition:
            composed_observable = test_composition
          else:
            if obj.attributes or obj.related_objects:
              # then the references are done differently
              # the object moves down into an other observable

              observable.event = None
              observable.event_id = None

              # create a new observable
              new_obs = Observable()

              new_obs.event = event
              new_obs.event_id = event.identifier
              new_obs.parent = event
              new_obs.parent_id = event.identifier
              new_obs.dbcode = observable.dbcode

              self.attribute_controller.set_extended_logging(new_obs, cache_object.user, True)

              composed_observable = ObservableComposition()
              composed_observable.uuid = uuid4()

              composed_observable.dbcode = observable.dbcode
              composed_observable.parent = new_obs

              new_obs.observable_composition = composed_observable

              new_obs.observable_composition.observables.append(observable)
              self.observable_controller.insert_observable(new_obs, cache_object.user, commit=False)
              first_obs = param_1.pop(0)
              first_object = first_obs.object
              for attr in first_object.attributes:
                observable.object.attributes.append(attr)
            else:
              # if the the object has no attributes and no related objects create a composed observable
              # if there exists none create composed observable
              composed_observable = ObservableComposition()
              composed_observable.uuid = uuid4()

              composed_observable.dbcode = observable.dbcode
              composed_observable.parent = observable

              observable.observable_composition = composed_observable

          for obs in param_1:
            # enforce that no parent is set
            obs.event = None
            obs.event_id = None
            obs.parent = event
            obs.parent_id = event.identifier
            # set extended logging
            self.attribute_controller.set_extended_logging(obs, cache_object.user, True)

            composed_observable.observables.append(obs)

          if test_composition:
            self.observable_controller.update_observable_compositon(composed_observable, cache_object.user, commit=False)
          else:
            self.observable_controller.update_observable(observable, cache_object.user, commit=False)
          param_1 = composed_observable.parent

        else:
          # process the attributes and related objects

          # get the main attribtue

          # Check if not elements were attached to the object
          # TODO: find a way to check if the object has been changed
          # TODO also check if there are no children attached
          if True:
            if param_1:
              self.attribute_controller.insert_attributes(param_1, cache_object.user, False, cache_object.owner)
              self.observable_controller.insert_handler_related_objects(related_objects, cache_object.user, False, cache_object.owner)
            else:
              # attach the related object to the parent object if there is any
              if obj.related_object_parent:
                # attach the related objects to the parent object!!
                parent_obj = self.observable_controller.get_parent_object_by_object(obj)
                if not obj.attributes:
                  first_relObject = related_objects.pop(0)
                  for attr in first_relObject.object.attributes:
                    attr.object = obj
                    attr.object_id = obj.identifier
                    obj.attributes.append(attr)
                  modified_obj = True
                for related_object in related_objects:
                  parent_obj.related_objects.append(related_object)
                self.observable_controller.update_object(parent_obj, cache_object.user, False)
                # self.observable_controller.insert_handler_related_objects(related_objects, user, False, self.is_event_owner(event, user))

              else:
                raise RestHandlerException('The object is a root object, cannot process this. Please ask for assistance')

          else:
            raise RestHandlerException('The object has been modified by the handler {0} this cannot be'.format(definition.attribute_handler.classname))

          # return the attributes and related objects

        # extract all the attributes to make relations
        flat_attriutes = self.__get_all_attribtues(param_1, related_objects, is_observable)
        if modified_obj:
          is_observable = True
          param_1 = obj.observable
        # make relations
        # TODO: add flag to skip this step
        self.relations_controller.generate_bulk_attributes_relations(event, flat_attriutes, True)

        result = self.__make_attribute_insert_return(param_1, related_objects, is_observable, cache_object)

        return result

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
            self.attribute_controller.update_attribute(attribute, cache_object.user, True)

            return attribute.to_dict(cache_object)
          elif method == 'DELETE':
            self.check_if_event_is_deletable(event)
            self.check_item_is_viewable(event, attribute)
            self.attribute_controller.remove_attribute(attribute, cache_object.user, True)
            return 'Deleted object'

    except ValueException as error:
      raise RestHandlerException(error)
