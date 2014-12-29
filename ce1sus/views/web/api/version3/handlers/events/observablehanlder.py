# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.object import Object
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, PathParsingException, RestHandlerException, RestHandlerNotFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.observable_controller = ObservableController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  def observable(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      # get the event
      observable_id = requested_object.get('event_id')
      if observable_id:
        observable = self.observable_controller.get_observable_by_id(observable_id)
        event = self.observable_controller.get_event_for_observable(observable)
        # check if event is viewable by the current user
        self.check_if_event_is_viewable(event)

        if requested_object['object_type'] is None:
          return self.__process_observable(method, event, observable, details, inflated, json)
        elif requested_object['object_type'] == 'object':
          flat = self.get_flat_value(args)
          return self.__process_object(method, event, observable, requested_object, details, inflated, json, flat)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Observable cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_observable(self, method, event, observable, details, inflated, json):
    user = self.get_user()
    if method == 'POST':
      raise RestHandlerException('Recurive observables are currently not supported')
    else:
      if method == 'GET':
        self.check_if_event_is_viewable(event)
        return observable.to_dict(details, inflated)
      elif method == 'PUT':
        self.check_if_event_is_modifiable(event)
        observable.populate(json)
        self.observable_controller.update_observable(observable, user, True)
        return observable.to_dict(details, inflated)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.observable_controller.remove_observable(observable, user, True)
        return 'Deleted observable'

  def __process_object(self, method, event, observable, requested_object, details, inflated, json, flat):
    user = self.get_user()
    if method == 'POST':
      self.check_if_user_can_add(event)
      obj = Object()
      obj.parent = observable
      obj.populate(json)
      obj.observable_id = observable.identifier
      self.observable_controller.insert_object(obj, user, True)
      return obj.to_dict(details, inflated)
    else:
      uuid = requested_object['object_uuid']
      if uuid:
        obj = self.observable_controller.get_object_by_id(uuid)
      else:
        if not flat:
          raise PathParsingException(u'object cannot be called without an ID')
      if method == 'GET':
        self.check_if_event_is_viewable(event)
        if flat:
          result = list()
          flat_objects = self.observable_controller.get_flat_observable_objects(observable)
          for flat_object in flat_objects:
            result.append(flat_object.to_dict(details, inflated))
          return result
        else:
          return self.__process_object_get(requested_object, details, inflated)
      elif method == 'PUT':
        obj.populate(json)
        self.observable_controller.update_object(obj, user, True)
        return obj.to_dict(details, inflated)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.observable_controller.remove_object(obj, user, True)
        return 'Deleted observable'
