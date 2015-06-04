# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.observables import Observable, ObservableComposition
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, PathParsingException, RestHandlerException, RestHandlerNotFoundException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.observable_controller = self.controller_factory(ObservableController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def observable(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      headers = args.get('headers')
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      # get the event
      observable_id = requested_object.get('event_id')
      if observable_id:
        observable = self.observable_controller.get_observable_by_uuid(observable_id)
        event = self.observable_controller.get_event_for_observable(observable)
        # check if event is viewable by the current user
        self.check_if_event_is_viewable(event)

        if requested_object['object_type'] is None:
          return self.__process_observable(method, event, observable, details, inflated, json, headers)
        elif requested_object['object_type'] == 'object':
          flat = self.get_flat_value(args)
          return self.__process_object(method, event, observable, requested_object, details, inflated, json, flat, headers)
        elif requested_object['object_type'] == 'observable':
          return self.__process_observable_child(method, event, observable, requested_object, details, inflated, json, headers)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Observable cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_observable_child(self, method, event, observable, requested_object, details, inflated, json, headers):
    user = self.get_user()
    event_permissions = self.get_event_user_permissions(event, user)
    if method == 'POST':
      self.check_if_user_can_add(event)
      child_obs = self.assembler.assemble_observable(event, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
      child_obs.event = None
      child_obs.event_id = None
      if observable.observable_composition:
        observable.observable_composition.observables.append(child_obs)
        self.observable_controller.update_observable(observable, user, True)
      else:
        # then it is a related observable
        pass
      return child_obs.to_dict(details, inflated, event_permissions, user)
    else:
      raise RestHandlerException('use observable/{uuid} instead')

  def __process_observable(self, method, event, observable, details, inflated, json, headers):
    user = self.get_user()
    event_permissions = self.get_event_user_permissions(event, user)
    if method == 'POST':
      raise RestHandlerException('Recurive observables are currently not supported')
    else:
      self.check_item_is_viewable(event, observable)
      if method == 'GET':

        return observable.to_dict(details, inflated, event_permissions, user)
      elif method == 'PUT':
        self.check_if_event_is_modifiable(event)
        self.check_if_user_can_set_validate_or_shared(event, observable, user, json)
        observable = self.assembler.update_observable(observable, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
        self.observable_controller.update_observable(observable, user, True)
        return observable.to_dict(details, inflated, event_permissions, user)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.observable_controller.remove_observable(observable, user, True)
        return 'Deleted observable'

  def __set_properties(self, obj, rest_insert, owner, parent):
    obj.properties.is_rest_instert = rest_insert
    obj.properties.is_web_insert = not rest_insert
    if owner:
      obj.properties.is_validated = True
      obj.properties.is_proposal = False
    else:
      obj.properties.is_validated = False
      obj.properties.is_proposal = True
    obj.properties.is_shareable = parent.properties.is_shareable

  def __process_object(self, method, event, observable, requested_object, details, inflated, json, flat, headers):
    user = self.get_user()
    event_permissions = self.get_event_user_permissions(event, user)
    if method == 'POST':
      self.check_if_user_can_add(event)
      rest_insert = self.is_rest_insert(headers)
      owner = self.is_event_owner(event, user)
      # check if observable has already an object
      if observable.object:

        obs = Observable()
        obs.event = event
        obs.tlp_level_id = observable.tlp_level_id
        obs.parent = event
        self.observable_controller.set_extended_logging(obs, user, user.group, True)
        self.__set_properties(obs, rest_insert, owner, observable)

        comp_obs = ObservableComposition()
        comp_obs.parent = obs
        obs.observable_composition = comp_obs
        comp_obs.tlp_level_id = observable.tlp_level_id
        self.__set_properties(comp_obs, rest_insert, owner, observable)

        child_obs = Observable()
        child_obs.parent = event
        child_obs.tlp_level_id = observable.tlp_level_id
        comp_obs.observables.append(child_obs)
        comp_obs.observables.append(observable)

        self.__set_properties(child_obs, rest_insert, owner, observable)
        self.observable_controller.set_extended_logging(child_obs, user, user.group, True)

        obj = self.assembler.assemble_object(child_obs, json, user, owner, rest_insert)

        child_obs.object = obj
        self.observable_controller.insert_observable(obs, user, True)
        observable.event = None
        observable.event_id = None

        self.observable_controller.insert_object(obj, user, False)
        # update observable
        self.observable_controller.update_observable(observable, user, True)
        return obs.to_dict(details, True, event_permissions, user)
      else:
        obj = self.assembler.assemble_object(observable, json, user, owner, rest_insert)
        self.observable_controller.insert_object(obj, user, True)
        return obj.to_dict(details, inflated, event_permissions, user)
    else:
      uuid = requested_object['object_uuid']
      if uuid:
        obj = self.observable_controller.get_object_by_uuid(uuid)
        self.check_item_is_viewable(event, obj)
      else:
        if not flat:
          raise PathParsingException(u'object cannot be called without an ID')
      if method == 'GET':
        if flat:
          result = list()
          flat_objects = self.observable_controller.get_flat_observable_objects(observable)
          for flat_object in flat_objects:
            result.append(flat_object.to_dict(details, inflated, event_permissions, user))
          return result
        else:
          return self.__process_object_get(requested_object, details, inflated)
      elif method == 'PUT':
        self.check_if_event_is_modifiable(event)
        self.check_if_user_can_set_validate_or_shared(event, obj, user, json)
        obj = self.assembler.update_object(obj, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
        self.observable_controller.update_object(obj, user, True)
        return obj.to_dict(details, inflated, event_permissions, user)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.observable_controller.remove_object(obj, user, True)
        return 'Deleted observable'
