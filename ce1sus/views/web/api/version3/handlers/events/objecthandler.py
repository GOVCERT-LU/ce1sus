# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""

from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.attributecontroller import AttributeController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.common import ValueException
from ce1sus.db.classes.object import Object, RelatedObject
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, PathParsingException, RestHandlerException, RestHandlerNotFoundException, require
from ce1sus.controllers.events.relations import RelationController
from ce1sus.handlers.base import HandlerException


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
    self.observable_controller = ObservableController(config)
    self.attribute_controller = AttributeController(config)
    self.attribute_definition_controller = AttributeDefinitionController(config)
    self.object_definition_controller = ObjectDefinitionController(config)
    self.relations_controller = RelationController(config)

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
          return obj.to_dict(details, inflated, event_permissions)
        elif method == 'PUT':
          self.check_if_event_is_modifiable(event)
          self.check_item_is_viewable(event, obj)
          self.check_if_user_can_set_validate_or_shared(event, obj, user, json)
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

          obj.populate(json, self.is_rest_insert(headers))
          self.observable_controller.update_object(obj, user, True)
          return obj.to_dict(details, inflated, event_permissions)
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
      child_obj = Object()
      child_obj.populate(json, self.is_rest_insert(headers))
      child_obj.observable_id = obj.observable_id
      self.observable_controller.insert_object(child_obj, user, False)

      # update parent
      related_object = RelatedObject()
      related_object.parent_id = obj.identifier
      related_object.child_id = child_obj.identifier
      related_object.object = child_obj
      related_object.relation = json.get('relation', None)
      if related_object.relation == 'None':
        related_object.relation = None
      obj.related_objects.append(related_object)
      self.observable_controller.update_object(child_obj, user, True)

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
    return handler_instance

  def __set_provenance(self, instance, headers):
    rest_insert = self.is_rest_insert(headers)
    instance.properties.is_rest_instert = rest_insert
    instance.properties.is_web_insert = not rest_insert

  def __process_attribute(self, method, event, obj, requested_object, details, inflated, json, headers):
    try:
      user = self.get_user()
      if method == 'POST':
        self.check_if_user_can_add(event)
        # Get needed handler
        definition = self.attribute_definition_controller.get_attribute_definitions_by_uuid(json.get('definition_id', None))
        handler_instance = self.__get_handler(definition)

        # Ask handler to process the json for the new attributes
        attribute, additional_attributes, related_objects = handler_instance.insert(obj, user, json)
        # Check if not elements were attached to the object
        # TODO: find a way to check if the object has been changed
        # TODO also check if there are no children attached
        if True:
          self.__set_provenance(attribute, headers)
          self.attribute_controller.insert_attribute(attribute, additional_attributes, user, False, self.is_event_owner(event, user))
          # set provenance
          if related_objects:
            for related_object in related_objects:
              self.__set_provenance(related_object, headers)
          self.observable_controller.insert_handler_objects(related_objects, user, True, self.is_event_owner(event, user))
        else:
          raise RestHandlerException('The object has been modified by the handler {0} this cannot be'.format(definition.attribute_handler.classname))

        # Make attributes flat
        flat_attriutes = list()

        # Return the generated attributes as json
        result_attriutes = list()
        flat_attriutes.append(attribute)
        result_attriutes.append(attribute.to_dict(details, inflated))
        if additional_attributes:
          for additional_attribute in additional_attributes:
            self.__set_provenance(additional_attribute, headers)
            flat_attriutes.append(flat_attriutes)
            result_attriutes.append(additional_attribute.to_dict(details, inflated))

        result_objects = list()
        if related_objects:
          for related_object in related_objects:
            # make the attributes of the related object flat
            flat_attriutes = flat_attriutes + self.relations_controller.make_object_attributes_flat(related_object)

            result_objects.append(related_object.to_dict(details, inflated))

        # make relations
        # TODO: add flag to skip this step
        self.relations_controller.generate_bulk_attributes_relations(event, flat_attriutes, True)

        return {'attributes': result_attriutes, 'related_objects': result_objects}

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
            self.check_if_event_is_modifiable(event)
            self.check_item_is_viewable(event, attribute)
            definition_uuid = json.get('definition_id', None)

            if definition_uuid:
              # check if it still is the same
              if attribute.definition.uuid != definition_uuid:
                raise HandlerException('It is not possible to change the definition of attribtues')

            handler_instance = self.__get_handler(attribute.definition)

            self.check_if_user_can_set_validate_or_shared(event, attribute, user, json)
            # Ask handler to process the json for the new attributes
            attribute = handler_instance.update(attribute, user, json)
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
