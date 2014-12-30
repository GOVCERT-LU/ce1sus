# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""

from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.attributecontroller import AttributeController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.attribute import Attribute
from ce1sus.db.classes.common import ValueException
from ce1sus.db.classes.object import Object, RelatedObject
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
    self.observable_controller = ObservableController(config)
    self.attribute_controller = AttributeController(config)
    self.attribute_definition_controller = AttributeDefinitionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def object(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      # get the event
      object_id = requested_object.get('event_id')
      obj = self.observable_controller.get_object_by_id(object_id)
      event = self.observable_controller.get_event_for_obj(obj)
      if object_id:
        if requested_object['object_type'] is None:
          # return the event

          # check if event is viewable by the current user
          self.check_if_event_is_viewable(event)
          return self.__process_object(method, event, obj, details, inflated, json)

        elif requested_object['object_type'] == 'object':
          return self.__process_child_object(method, event, obj, requested_object, details, inflated, json)
        elif requested_object['object_type'] == 'attribute':
          return self.__process_attribute(method, event, obj, requested_object, details, inflated, json)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Object cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_object(self, method, event, obj, details, inflated, json):
    try:
      user = self.get_user()
      if method == 'POST':
        raise RestHandlerException('Please use observable/{uuid}/instead')
      else:
        if method == 'GET':
          self.check_if_event_is_viewable(event)
          return obj.to_dict(details, inflated)
        elif method == 'PUT':
          self.check_if_event_is_modifiable(event)
          self.check_if_user_can_set_validate_or_shared(event, obj, user, json)
          # check if there was not a parent set
          parent_id = json.get('parent_object_id', None)
          if parent_id:
            # get related object
            related_object = self.observable_controller.get_related_object_by_child(obj)
            related_object.parent_id = parent_id
            related_object.relation = json.get('relation', None)
            self.observable_controller.update_related_object(related_object, user, False)
          obj.populate(json)
          self.observable_controller.update_object(obj, user, True)
          return obj.to_dict(details, inflated)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          self.observable_controller.remove_object(obj, user, True)
          return 'Deleted object'
    except ValueException as error:
      raise RestHandlerException(error)

  def __process_child_object(self, method, event, obj, requested_object, details, inflated, json):
    user = self.get_user()
    if method == 'POST':
      child_obj = Object()
      child_obj.populate(json)
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

  def __process_attribute(self, method, event, obj, requested_object, details, inflated, json):
    try:
      user = self.get_user()
      if method == 'POST':
        self.check_if_user_can_add(event)
        attribute = Attribute()
        # Imporant to set the definition else the set value wont work
        definition = self.attribute_definition_controller.get_attribute_definitions_by_id(json.get('definition_id', None))
        attribute.definition = definition
        # Important to set the parent object
        attribute.object = obj
        attribute.object_id = obj.identifier
        # set the remaining stuff
        attribute.populate(json)
        if self.is_event_owner(event, user):
          # The attribute is directly validated as the owner can validate
          attribute.properties.is_validated = True
        self.attribute_controller.insert_attribute(attribute, user, True)
        return attribute.to_dict(details, inflated)
      else:
        uuid = requested_object['object_uuid']
        if method == 'GET':
          if uuid:
            attribute = self.attribute_controller.get_attribute_by_id(uuid)
            self.check_if_event_is_viewable(event)
            return attribute.to_dict(details, inflated)
          else:
            result = list()
            for attribute in obj.attributes:
              result.append(attribute.to_dict(details, inflated))
            return result
        else:
          attribute = self.attribute_controller.get_attribute_by_id(uuid)
          if method == 'PUT':
            self.check_if_event_is_modifiable(event)
            self.check_if_user_can_set_validate_or_shared(event, attribute, user, json)
            attribute.populate(json)
            self.attribute_controller.update_attribute(attribute, user, True)
            return attribute.to_dict(details, inflated)
          elif method == 'DELETE':
            self.check_if_event_is_deletable(event)
            self.attribute_controller.remove_attribute(attribute, user, True)
            return 'Deleted object'

    except ValueException as error:
      raise RestHandlerException(error)
