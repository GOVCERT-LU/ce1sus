# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.object import Object, RelatedObject
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, PathParsingException, RestHandlerException, RestHandlerNotFoundException


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
    self.object_definition_broker = ObjectDefinitionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
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
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Object cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_object(self, method, event, obj, details, inflated, json):
    user = self.get_user()
    if method == 'POST':
      raise RestHandlerException('Please use observable/{uuid}/instead')
    else:
      if method == 'GET':
        self.check_if_event_is_viewable(event)
        return obj.to_dict(details, inflated)
      elif method == 'PUT':
        # check if there was not a parent set
        parent_id = json.get('parent_object_id', None)
        if parent_id:
          # get related object
          related_object = self.observable_controller.get_related_object_by_child(obj)
          related_object.parent_id = parent_id
          self.observable_controller.update_related_object(related_object, user, False)

        obj.populate(json)
        self.observable_controller.update_object(obj, user, True)
        return obj.to_dict(details, inflated)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.observable_controller.remove_object(obj, user, True)
        return 'Deleted object'

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
      object_id = requested_object['object_uuid']
      if object_id:
        child_obj = self.observable_controller.get_object_by_id(object_id)
      else:
        raise PathParsingException(u'object cannot be called without an ID')
      if method == 'GET':
        self.check_if_event_is_viewable(event)
        return child_obj.to_dict(details, inflated)
      elif method == 'PUT':
        self.check_if_event_is_modifiable(event)
        child_obj.populate(json)
        self.observable_controller.update_object(child_obj, user, True)
        return child_obj.to_dict(details, inflated)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.observable_controller.remove_object(child_obj, user, True)
        return 'Deleted object'
