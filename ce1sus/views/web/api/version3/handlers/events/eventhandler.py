# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
import cherrypy

from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.event import Event, Comment
from ce1sus.db.classes.observables import Observable
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException, RestHandlerNotFoundException, PathParsingException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.observable_controller = ObservableController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  def event(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      # get the event
      event_id = requested_object.get('event_id')
      if event_id:
        event = self.event_controller.get_event_by_id(event_id)
        # check if event is viewable by the current user
        self.check_if_event_is_viewable(event)

        if requested_object['object_type'] is None:
          # return the event
          return self.__process_event(method, event, details, inflated, json)
        elif requested_object['object_type'] == 'observable':
          return self.__process_observable(method, event, requested_object, details, inflated, json)
        elif requested_object['object_type'] == 'observable_composition':
          return self.__process_composed_observable(method, event, requested_object, details, inflated, json)
        elif requested_object['object_type'] == 'changegroup':
          self.check_if_admin()
          return self.__change_event_group(method, event, json)
        elif requested_object['object_type'] == 'comment':
          return self.__process_commment(method, event, requested_object, details, inflated, json)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        # This can only happen when a new event is inserted
        if method == 'POST':
          # populate event
          event = Event()
          event.populate(json)
          # TODO: make relations an populate the whole event by json
          user = self.get_user()
          if self.is_event_owner(event, user):
            # The observable is directly validated as the owner can validate
            event.properties.is_validated = True
          self.event_controller.insert_event(user, event, True, True)
          return self.__return_event(event, details, inflated)
        else:
          raise RestHandlerException(u'Invalid request - Event cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __is_event_ovner(self, method, event):
    if method == 'GET':
      return self.is_event_owner(event, self.get_user())
    else:
      raise RestHandlerException(u'Invalid request')

  def __change_event_group(self, method, event, json):
    if method == 'PUT':
      if self.is_user_priviledged(self.get_user()):
        group_id = json.get('identifier', None)
        self.event_controller.change_owner(event, group_id, self.get_user())

        return 'OK'
      else:
        # TODO: make this cleaner
        raise cherrypy.HTTPError(403, 'No allowed')
    else:
      raise RestHandlerException(u'Invalid request')

  def __process_commment(self, method, event, requested_object, details, inflated, json):
    self.check_if_owner(event)
    user = self.get_user()
    if method == 'POST':
      comment = Comment()
      comment.populate(json)
      comment.event_id = event.identifier
      self.event_controller.insert_comment(user, comment)
      return comment.to_dict(details, inflated)
    else:
      comment_id = requested_object['object_uuid']
      if comment_id:
        comment = self.event_controller.get_comment_by_id(comment_id)
      else:
        raise PathParsingException(u'comment cannot be called without an ID')
      if method == 'GET':
        return comment.to_dict(details, inflated)
      elif method == 'PUT':
        comment.populate(json)
        self.event_controller.update_comment(user, comment)
        return comment.to_dict(details, inflated)
      elif method == 'DELETE':
        self.event_controller.remove_comment(user, comment)
        return 'Deleted comment'
      else:
        raise RestHandlerException(u'Invalid request')

  def __process_event(self, method, event, details, inflated, json):
    if method == 'GET':
      return self.__return_event(event, details, inflated)
    elif method == 'POST':
      # this cannot happen here
      raise RestHandlerException(u'Invalid request')
    elif method == 'PUT':
      user = self.get_user()
      self.check_if_event_is_modifiable(event)
      # check if validated / shared as only the owner can do this
      self.check_if_user_can_set_validate_or_shared(event, event, user, json)

      event.populate(json)
      # TODO: make relations an populate the whole event by json
      self.event_controller.update_event(user, event, True, True)
      return self.__return_event(event, details, inflated)
    elif method == 'DELETE':
      self.check_if_event_is_deletable(event)
      self.event_controller.remove_event(self.get_user(), event)
      return 'Deleted event'

  def __process_observable(self, method, event, requested_object, details, inflated, json):
    user = self.get_user()
    if method == 'POST':
      self.check_if_user_can_add(event)
      observable = Observable()
      observable.event_id = event.identifier
      observable.populate(json)
      observable.parent_id = event.identifier
      if self.is_event_owner(event, user):
        # The observable is directly validated as the owner can validate
        observable.properties.is_validated = True

      self.observable_controller.insert_observable(observable, user, True)
      return observable.to_dict(details, inflated)
    else:
      if method == 'GET':
        self.check_if_event_is_viewable(event)
        return self.__process_observable_get(event, requested_object, details, inflated)
      else:
        observable_id = requested_object['object_uuid']
        if observable_id:
          observable = self.observable_controller.get_observable_by_id(observable_id)
        else:
          raise PathParsingException(u'observale cannot be called without an ID')
        if method == 'PUT':
          self.check_if_event_is_modifiable(event)
          self.check_if_user_can_set_validate_or_shared(event, observable, user, json)
          observable.populate(json)
          self.observable_controller.update_observable(observable, user, True)
          return observable.to_dict(details, inflated)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          self.observable_controller.remove_observable(observable, user, True)
          return 'Deleted observable'

  def __process_observable_get(self, event, requested_object, details, inflated):
    try:
      uuid = requested_object['object_uuid']
      if uuid:
        # return the given observable
        # TODO: Check if observable belongs to event
        observable = self.observable_controller.get_observable_by_id(uuid)
        return observable.to_dict(details, inflated)
      else:
        # return all observables from the event
        result = list()
        for observable in event.observables:
          result.append(observable.to_dict(details, inflated))
        return result
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_composed_observable(self, method, event, requested_object, details, inflated, json):
    if method == 'GET':
      return self.__process_composed_observable_get(requested_object, details, inflated)
    elif method == 'POST':
      raise RestHandlerException('Operation not supported')
    elif method == 'PUT':
      raise RestHandlerException('Operation not supported')
    elif method == 'DELETE':
      self.event_controller.remove_event(self.get_user(), event)

  def __process_composed_observable_get(self, requested_object, details, inflated):
    try:
      uuid = requested_object['object_uuid']
      if uuid:
        composed_observable = self.observable_controller.get_composed_observable_by_id(uuid)
        return composed_observable.to_dict(details, inflated)
      else:
        raise PathParsingException(u'observable_composition cannot be called without an ID')
    except ControllerException as error:
      raise RestHandlerException(error)

  def __return_event(self, event, details, inflated):
    # Add additional permissions for the user itsel
    user = self.get_user()
    event_permission = self.event_controller.get_event_user_permissions(event, user)
    result = event.to_dict(details, inflated)
    result['userpermissions'] = event_permission.to_dict()
    result['userpermissions']['owner'] = self.is_event_owner(event, user)
    return result

  """
  @rest_method()
  @methods(allowed=['GET'])
  def stix_import(self, **args):
    stix_package = STIXPackage.from_xml('/home/jhemp/Downloads/CIMBL-150-CERTS.xml')
    user = self.user_broker.get_all()[0]
    event = self.stix_mapper.map_stix_package(stix_package, user)
    self.event_controller.insert_event(user, event)
    pass
  """
