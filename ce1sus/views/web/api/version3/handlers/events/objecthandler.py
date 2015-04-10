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
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.common import ValueException
from ce1sus.db.classes.observables import ObservableComposition, Observable
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
    RestBaseHandler.__init__(self, config)
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
      details = self.get_detail_value(args)
      headers = args.get('headers')
      inflated = self.get_inflated_value(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      # get the event
      object_id = requested_object.get('event_id')
      if object_id:
        obj = self.observable_controller.get_object_by_uuid(object_id)
        event = obj.event
        self.check_if_event_is_viewable(event)
        if requested_object['object_type'] is None:
          # return the event

          # check if event is viewable by the current user

          return self.__process_object(method, event, obj, details, inflated, json, headers)

        elif requested_object['object_type'] == 'object':
          return self.__process_child_object(method, event, obj, requested_object, details, inflated, json, headers)
        elif requested_object['object_type'] == 'attribute':
          return self.__process_attribute(method, event, obj, requested_object, details, inflated, json, headers)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Object cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_object(self, method, event, obj, details, inflated, json, headers):
    try:
      user = self.get_user()
      if method == 'POST':
        raise RestHandlerException('Please use observable/{uuid}/instead')
      else:
        event_permissions = self.get_event_user_permissions(event, self.get_user())
        if method == 'GET':
          self.check_item_is_viewable(event, obj)
          return obj.to_dict(details, inflated, event_permissions, user)
        elif method == 'PUT':
          old_obj = obj
          self.check_if_event_is_modifiable(event)
          self.check_item_is_viewable(event, obj)
          self.check_if_user_can_set_validate_or_shared(event, old_obj, user, json)
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
              self.observable_controller.update_related_object(related_object, user, False)
          obj = self.assembler.update_object(obj, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
          self.observable_controller.update_object(obj, user, True)
          return obj.to_dict(details, inflated, event_permissions, user)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          self.check_item_is_viewable(event, obj)
          self.observable_controller.remove_object(obj, user, True)
          return 'Deleted object'
    except ValueException as error:
      raise RestHandlerException(error)

  def __process_child_object(self, method, event, obj, requested_object, details, inflated, json, headers):
    user = self.get_user()
    if method == 'POST':
      self.check_if_user_can_add(event)
      related_object = self.assembler.assemble_related_object(obj, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
      self.observable_controller.update_object(related_object.object, user, True)

      return related_object.to_dict(details, inflated)
    else:
      raise RestHandlerException('Please use object/{uuid}/ instead')

  def __get_handler(self, definition):
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
      additional_obj_definitions = self.object_definition_broker.get_defintion_by_chksums(additional_obj_defs_chksums)
      for additional_obj_definition in additional_obj_definitions:
        handler_instance.object_definitions[additional_obj_definition.chksum] = additional_obj_definition

    handler_instance.user = self.get_user()

    # set conditions
    conditions = self.conditions_controller.get_all_conditions()
    handler_instance.conditions = conditions

    return handler_instance

  def __make_attribute_insert_return(self, param_1, related_objects, observable, is_observable, details, inflated):
    if is_observable:
      return {'observable': param_1.to_dict(), 'relpaced_observable': observable.to_dict(False, False)}
    else:
      result_attriutes = list()
      result_objects = list()
      for attr in param_1:
        result_attriutes.append(attr.to_dict(details, inflated))
      if related_objects:
        for related_object in related_objects:
          result_objects.append(related_object.to_dict(details, inflated))
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
    if obs.related_observables:
      for rel_obs in obs.related_observables:
        result = result + self.__get_attribtues_for_observable(rel_obs.observable)

    return result

  def __get_all_attribtues(self, param_1, related_objects, is_observable):
    result = list()
    if is_observable:
      # then param 1 is an wrapped composed observable
      for obs in param_1.observable_composition.observables:
        result = result + self.__get_attribtues_for_observable(obs)
    else:
      result = result + param_1
      if related_objects:
        for rel_obj in related_objects:
          result = result + self.__get_attribtues_for_object(rel_obj)
    return result

  def __process_attribute(self, method, event, obj, requested_object, details, inflated, json, headers):
    try:
      user = self.get_user()
      if method == 'POST':
        self.check_if_user_can_add(event)
        # Get needed handler
        definition = self.attribute_definition_controller.get_attribute_definitions_by_uuid(json.get('definition_id', None))
        handler_instance = self.__get_handler(definition)
        # set provenace to handler
        handler_instance.is_rest_insert = self.is_rest_insert(headers)
        handler_instance.is_owner = self.is_event_owner(event, user)
        # Ask handler to process the json for the new attributes/observables
        # param 1 can be either a list of attributes or a list of observables
        param_1, related_objects = handler_instance.insert(obj, user, json)

        is_observable = True
        # checks for param 1:
        if isinstance(param_1, ListType):
          if len(param_1) > 0:
            first_element = param_1[0]
            if isinstance(first_element, Attribute):
              is_observable = False
            else:
              if related_objects:
                raise RestHandlerException('Handler  {0} returns observables but also related objects this cannot be'.format(definition.attribute_handler.classname))
          else:
            raise RestHandlerException('Fist parameter is an empty list for handler {0}'.format(definition.attribute_handler.classname))
        else:
          raise RestHandlerException('Fist parameter is not a list for handler {0}'.format(definition.attribute_handler.classname))

        if is_observable:
          # make a composed observable for the observables gotten an the observable of the originating object
          observable = obj.observable

          # check if there is already a composed observable on top
          try:
            test_composition = self.observable_controller.get_composition_by_observable(observable)
          except ControllerNothingFoundException:
            test_composition = None

          if test_composition:
            composed_observable = test_composition
          else:
            # if there exists none create composed observable
            composed_observable = ObservableComposition()
            composed_observable.uuid = uuid4()

            composed_observable.dbcode = observable.dbcode

          # only add if there are attributes
          if obj.attributes:
            composed_observable.observables.append(observable)

          # TODO: check if the obseravbles are valid
          for obs in param_1:
            # enforce that no parent is set
            obs.event = None
            obs.event_id = None
            obs.parent = observable.parent
            obs.parent_id = observable.parent_id
            # set extended logging
            db_user = user = self.attribute_controller.user_broker.get_by_id(user.identifier)
            self.attribute_controller.set_extended_logging(obs, db_user, db_user.group, True)

            composed_observable.observables.append(obs)

          # wrapper for composed observable
          if test_composition:
            wrapped_observable = composed_observable.parent
            replaced_observable = test_composition.parent
          else:
            wrapped_observable = Observable()
            wrapped_observable.uuid = uuid4()
            wrapped_observable.observable_composition = composed_observable

            wrapped_observable.event = observable.event
            wrapped_observable.event_id = observable.event_id
            wrapped_observable.parent = observable.parent
            wrapped_observable.parent_id = observable.parent_id
            wrapped_observable.dbcode = observable.dbcode

            composed_observable.parent = wrapped_observable
            composed_observable.parent_id = wrapped_observable.identifier

            observable.event_id = None
            observable.event = None

            replaced_observable = observable

          # insert composed observable
          self.observable_controller.insert_composed_observable(wrapped_observable, user, False, self.is_event_owner(event, user))

          param_1 = wrapped_observable
        else:
          replaced_observable = None
          # process the attributes and related objects

          # get the main attribtue

          # Check if not elements were attached to the object
          # TODO: find a way to check if the object has been changed
          # TODO also check if there are no children attached
          if True:
            self.attribute_controller.insert_attributes(param_1, user, False, self.is_event_owner(event, user))
            self.observable_controller.insert_handler_objects(related_objects, user, False, self.is_event_owner(event, user))

          else:
            raise RestHandlerException('The object has been modified by the handler {0} this cannot be'.format(definition.attribute_handler.classname))

          # return the attributes and related objects

        # extract all the attributes to make relations
        flat_attriutes = self.__get_all_attribtues(param_1, related_objects, is_observable)

        # make relations
        # TODO: add flag to skip this step
        self.relations_controller.generate_bulk_attributes_relations(event, flat_attriutes, True)

        result = self.__make_attribute_insert_return(param_1, related_objects, replaced_observable, is_observable, details, inflated)
        # clean up
        if not obj.attributes:
          # remove the empty attribute
          self.observable_controller.remove_observable(obj.observable, user)

        return result

      else:
        uuid = requested_object['object_uuid']
        if method == 'GET':
          if uuid:
            attribute = self.attribute_controller.get_attribute_by_uuid(uuid)
            self.check_item_is_viewable(event, attribute)
            return attribute.to_dict(details, inflated)
          else:
            result = list()
            for attribute in obj.attributes:
              if self.is_item_viewable(event, attribute):
                result.append(attribute.to_dict(details, inflated))
            return result
        else:
          attribute = self.attribute_controller.get_attribute_by_uuid(uuid)
          if method == 'PUT':
            old_attr = attribute
            self.check_if_event_is_modifiable(event)
            self.check_item_is_viewable(event, attribute)
            self.check_if_user_can_set_validate_or_shared(event, old_attr, user, json)
            definition_uuid = json.get('definition_id', None)

            if definition_uuid:
              # check if it still is the same
              if attribute.definition.uuid != definition_uuid:
                raise HandlerException('It is not possible to change the definition of attribtues')

            handler_instance = self.__get_handler(attribute.definition)
            handler_instance.is_rest_insert = self.is_rest_insert(headers)
            handler_instance.is_owner = self.is_event_owner(event, user)

            # Ask handler to process the json for the new attributes
            attribute = handler_instance.update(attribute, user, json)

            if self.is_event_owner(event, user):
              attribute.properties.is_validated = True
              attribute.properties.is_proposal = False
            else:
              attribute.properties.is_validated = False
              attribute.properties.is_proposal = True

            self.logger.info(u'User {0} changed attribute {1} from {2} to {3}'.format(user.username, attribute.identifier, old_attr.value, attribute.value))

            # TODO: check if there are no children attached
            self.attribute_controller.update_attribute(attribute, user, True)

            return attribute.to_dict(details, inflated)
          elif method == 'DELETE':
            self.check_if_event_is_deletable(event)
            self.check_item_is_viewable(event, attribute)
            self.attribute_controller.remove_attribute(attribute, user, True)
            return 'Deleted object'

    except ValueException as error:
      raise RestHandlerException(error)
