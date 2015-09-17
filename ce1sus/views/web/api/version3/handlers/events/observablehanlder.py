# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 22, 2014
"""
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException, NotImplementedException
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.internal.object import Object
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, PathParsingException, RestHandlerException, RestHandlerNotFoundException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ObservableHandler(RestBaseHandler):

  def __init__(self, config):
    super(ObservableHandler, self).__init__(config)
    self.observable_controller = self.controller_factory(ObservableController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def observable(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      cache_object = self.get_cache_object(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      # get the event
      observable_id = requested_object.get('event_id')
      if observable_id:
        observable = self.observable_controller.get_observable_by_uuid(observable_id)
        event = self.observable_controller.get_event_for_observable(observable)
        # check if event is viewable by the current user
        self.set_event_properties_cache_object(cache_object, event)
        self.check_if_instance_is_viewable(event, cache_object)
        self.check_if_instance_is_viewable(observable, cache_object)

        if requested_object['object_type'] is None:
          return self.__process_observable(method, event, observable, json, cache_object)
        elif requested_object['object_type'] == 'object':
          return self.__process_object(method, event, observable, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'observable':
          return self.__process_observablecomposition(method, event, observable, requested_object, json, cache_object)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))
      else:
        raise RestHandlerException(u'Invalid request - Observable cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_observablecomposition(self, method, event, observable, requested_object, json, cache_object):
    if method == 'POST':
      # TODO make an observable composition handler this is only temporary
      child_observable = self.assembler.assemble(json, Observable, observable.observable_composition, cache_object)
      observable.observable_composition.observables.append(child_observable)
      self.observable_controller.update_observable(observable, cache_object, True)
      cache_object.inflated = True
      return child_observable.to_dict(cache_object)
    else:
      raise RestHandlerException('Method {0} is not available'.format(method))

  def __process_observable(self, method, event, observable, json, cache_object):
    if method == 'POST':
      raise RestHandlerException('Please use event/{uuid}/observable instead')
    else:
      self.check_item_is_viewable(event, observable)
      if method == 'GET':
        return observable.to_dict(cache_object)
      elif method == 'PUT':
        self.check_if_is_modifiable(event, cache_object)
        self.check_allowed_set_validate_or_shared(event, observable, cache_object, json)
        self.updater.update(observable, json, cache_object)
        self.observable_controller.update_observable(observable, cache_object, True)
        return observable.to_dict(cache_object)
      elif method == 'DELETE':
        self.check_if_is_deletable(event, cache_object)
        self.observable_controller.remove_observable(observable, cache_object, True)
        return 'Deleted observable'

  def __process_object(self, method, event, observable, requested_object, json, cache_object):
    if method == 'POST':
      if observable.object:
        # check if observable has already an object
        obj = self.assembler.assemble(json, Object, observable, cache_object)
        obs = self.observable_controller.insert_composed_observable_object(obj, observable, cache_object, commit=True)
        cache_object.inflated = True
        return obs.to_dict(cache_object)
      else:
        obj = self.assembler.assemble(json, Object, observable, cache_object)
        if obj:
          self.observable_controller.insert_object(obj, cache_object, commit=True)
          return obj.to_dict(cache_object)
        # save the errors
        self.event_controller.event_broker.do_commit(True)
        raise RestHandlerException('Error occured during insert see error log')
    else:
      uuid = requested_object['object_uuid']
      if uuid:
        obj = self.observable_controller.get_object_by_uuid(uuid)
        self.check_if_instance_is_viewable(obj, cache_object)
      else:
        if not cache_object.flat:
          raise PathParsingException(u'object cannot be called without an ID')

      if method == 'GET':
        if cache_object.flat:
          raise NotImplementedException('Flat objects are not suported')
        else:
          if self.is_instance_viewable(observable.object, cache_object):
            return observable.object.to_dict(cache_object)
          else:
            raise ControllerNothingFoundException(u'Cannot find object with uuid {0}'.format(uuid)) 

      elif method == 'PUT':
        self.check_if_is_modifiable(event, cache_object)
        self.check_allowed_set_validate_or_shared(event, obj, cache_object, json)
        self.updater.update(obj, json, cache_object)
        self.observable_controller.update_object(obj, cache_object, True)
        return obj.to_dict(cache_object)
      elif method == 'DELETE':
        self.check_if_is_deletable(event, cache_object)
        self.observable_controller.remove_object(obj, cache_object, True)
        return 'Deleted object'
