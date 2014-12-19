# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
import re

from ce1sus.controllers.base import ControllerException
from ce1sus.controllers.events.event import EventController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.brokers.permissions.user import UserBroker
from ce1sus.db.classes.event import Event
from ce1sus.mappers.stix.stixmapper import StixMapper
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def valid_uuid(uuid):
  regex = re.compile('^[a-f0-9]{8}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{4}-?[a-f0-9]{12}\Z', re.I)
  match = regex.match(uuid)
  return bool(match)


class PathParsingException(RestHandlerException):
  pass


class EventHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.stix_mapper = StixMapper(config)
    self.event_controller = EventController(config)
    self.observable_controller = ObservableController(config)
    self.user_broker = self.event_controller.broker_factory(UserBroker)

  def __parse_path(self, path, method):
    """
    the path can either be empty or belongs to one of the following structures
    uuid/observable
    uuid/composed_observable
    uuid/object
    uuid/attribute

    uuid/observable/uuid
    uuid/composed_observable/uuid
    uuid/object/uuid
    uuid/attribute/uuid

    Everything else will be ignored
    """
    result = {'event_id': None,  # uuid of the event
              'object_type': None,
              'object_uuid': None,
              'sub_object': None
              }
    if len(path) > 0:
      event_id = path.pop(0)
      if valid_uuid(event_id):
        result['event_id'] = event_id
      else:
        raise PathParsingException(u'{0} is not a valid uuid'.format(event_id))
      if len(path) > 0:
        object_type = path.pop(0)
        result['object_type'] = object_type
      if len(path) > 0:
        object_uuid = path.pop(0)
        if valid_uuid(object_uuid):
          result['object_uuid'] = object_uuid
        else:
          raise PathParsingException(u'{0} is not a valid uuid'.format(object_uuid))
      if len(path) > 0:
        if method == 'POST':
          # can only be used for post to elements
          sub_object = path.pop(0)
          result['sub_object'] = sub_object
        else:
          raise PathParsingException(u'Path is too long')
      if len(path) > 0:
        raise PathParsingException(u'Path is too long')
    return result

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  def event(self, **args):
    method = args.get('method', None)
    path = args.get('path')
    details = self.get_detail_value(args)
    inflated = self.get_inflated_value(args)
    requested_object = self.__parse_path(path, method)
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
        return self.__process_composed_observable(requested_object, details, inflated, json)
      elif requested_object['object_type'] == 'object':
        return self.__process_object(requested_object, details, inflated, json)
      elif requested_object['object_type'] == 'attribute':
        return self.__process_attribute(requested_object, details, inflated, json)
      else:
        raise PathParsingException(u'{0} is not definied'.format(requested_object['object_type']))

    else:
      # This can only happen when a new event is inserted
      if method == 'POST':
        # populate event
        event = Event()
        event.populate(json)
        # TODO: make relations an populate the whole event by json
        self.event_controller.insert_event(self.get_user(), event, True, True)
        return event.to_dict(details, inflated)
      else:
        raise RestHandlerException(u'Invalid request')

  def __process_event(self, method, event, details, inflated, json):
    if method == 'GET':
      return event.to_dict(details, inflated)
    elif method == 'POST':
      # this cannot happen here
      raise RestHandlerException(u'Invalid request')
    elif method == 'PUT':
      event.populate(json)
      # TODO: make relations an populate the whole event by json
      self.event_controller.update_event(self.get_user(), event, True, True)
      return event.to_dict(details, inflated)
    elif method == 'DELETE':
      self.event_controller.remove_event(self.get_user(), event)
      return 'Deleted event'

  def __process_observable(self, method, event, requested_object, details, inflated, json):
    if method == 'GET':
      return self.__process_observable_get(event, requested_object, details, inflated)
    elif method == 'POST':
      pass
    elif method == 'PUT':
      pass
    elif method == 'DELETE':
      pass

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

  def __process_composed_observable(self, method, requested_object, details, inflated, json):
    if method == 'GET':
      return self.__process_composed_observable_get(requested_object, details, inflated)
    elif method == 'POST':
      pass
    elif method == 'PUT':
      pass
    elif method == 'DELETE':
      pass

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

  def __process_object(self, method, requested_object, details, inflated, json):
    if method == 'GET':
      return self.__process_object_get(requested_object, details, inflated)
    elif method == 'POST':
      pass
    elif method == 'PUT':
      pass
    elif method == 'DELETE':
      pass

  def __process_object_get(self, requested_object, details, inflated):
    try:
      uuid = requested_object['object_uuid']
      if uuid:
        obj = self.observable_controller.get_object_by_id(uuid)
        return obj.to_dict(details, inflated)
      else:
        raise PathParsingException(u'object cannot be called without an ID')
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_attribute(self, method, requested_object, details, inflated, json):
    if method == 'GET':
      return self.__process_attribute_get(requested_object, details, inflated)
    elif method == 'POST':
      pass
    elif method == 'PUT':
      pass
    elif method == 'DELETE':
      pass

  def __process_attribute_get(self, requested_object, details, inflated):
    try:
      uuid = requested_object['object_uuid']
      if uuid:
        obj = self.observable_controller.get_attribute_by_id(uuid)
        return obj.to_dict(details, inflated)
      else:
        raise PathParsingException(u'object cannot be called without an ID')
    except ControllerException as error:
      raise RestHandlerException(error)

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
