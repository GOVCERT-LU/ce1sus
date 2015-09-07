# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
import cherrypy

from ce1sus.controllers.admin.syncserver import SyncServerController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.controllers.common.process import ProcessController
from ce1sus.controllers.events.indicatorcontroller import IndicatorController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.controllers.events.reports import ReportController
from ce1sus.db.classes.ccybox.core.observables import Observable
from ce1sus.db.classes.internal.backend.processitem import ProcessType
from ce1sus.db.classes.internal.event import EventGroupPermission, Comment, Event
from ce1sus.db.classes.internal.report import Report
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException, RestHandlerNotFoundException, PathParsingException, require
from ce1sus.db.classes.internal.usrmgt.group import EventPermissions


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventHandler(RestBaseHandler):

  def __init__(self, config):
    super(EventHandler, self).__init__(config)
    self.observable_controller = self.controller_factory(ObservableController)
    self.relation_controller = self.controller_factory(RelationController)
    self.report_controller = self.controller_factory(ReportController)
    self.indicator_controller = self.controller_factory(IndicatorController)
    self.process_controller = self.controller_factory(ProcessController)
    self.server_controller = self.controller_factory(SyncServerController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def event(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      cache_object = self.get_cache_object(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')

      # get the event
      event_id = requested_object.get('event_id')
      if event_id:
        event = self.event_controller.get_event_by_uuid(event_id)
        # check if event is viewable by the current user
        self.set_event_properties_cache_object(cache_object, event)
        self.check_if_instance_is_viewable(event, cache_object)

        if requested_object['object_type'] is None:
                    # return the event
          return self.__process_event(method, event, json, cache_object)
        elif requested_object['object_type'] == 'observable':
          return self.__process_observable(method, event, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'indicator':
          return self.__process_indicator(method, event, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'changegroup':
          self.check_if_instance_owner(event, cache_object)
          return self.__change_event_group(method, event, json, cache_object)
        elif requested_object['object_type'] == 'comment':
          return self.__process_commment(method, event, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'publish':
          return self.__publish_event(method, event, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'validate':
          return self.__process_event_validate(method, event, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'group':
          return self.__process_event_group(method, event, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'relations':
          return self.__process_event_relations(method, event, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'report':
          return self.__process_event_report(method, event, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'errors':
          return self.__process_event_errors(method, event, requested_object, json, cache_object)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        # This can only happen when a new event is inserted
        if method == 'POST':
          # populate event
          cache_object.owner = True
          cache_object.event_permissions = EventPermissions('0')
          cache_object.event_permissions.set_all()

          event = self.assembler.assemble(json, Event, None, cache_object)

          self.event_controller.insert_event(event, cache_object, True, True)

          return self.__return_event(event, cache_object)
        else:
          raise RestHandlerException(u'Invalid request - Event cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_event_errors(self, method, event, requested_object, json, cache_object):
    self.check_if_instance_owner(event, cache_object)
    if method == 'POST':
      pass
    else:
      uuid = requested_object['object_uuid']
      if uuid:
        error = self.event_controller.get_error_by_uuid(uuid)
        if self.is_instance_viewable(error, cache_object):
          return error.to_dict(cache_object)
        else:
          raise ControllerNothingFoundException(u'Cannot find error with uuid {0}'.format(uuid))
      else:
        #list all
        result = event.attributelist_to_dict('errors', cache_object)
        if result is None:
          return list()
        else:
          return result

  def __change_event_group(self, method, event, json, cache_object):
    self.check_if_instance_owner(event, cache_object)
    if method == 'PUT':
      if self.is_user_priviledged(cache_object.user):
        group_id = json.get('identifier', None)
        self.event_controller.change_owner(event, group_id, cache_object)

        return 'OK'
      else:
        raise cherrypy.HTTPError(403, 'No allowed')
    else:
      raise RestHandlerException(u'Invalid request')

  def __process_commment(self, method, event, requested_object, json, cache_object):
    self.check_if_instance_owner(event, cache_object)
    if method == 'POST':
      comment = self.assembler.assemble(json, Comment, event, cache_object)
      self.event_controller.insert_comment(comment, cache_object)
      return comment.to_dict(cache_object)
    else:
      comment_id = requested_object['object_uuid']
      if method == 'GET' and not comment_id:
        # Return all comments
        cache_object.inflated = True
        result = event.attributelist_to_dict('comments', cache_object)
        if result:
          return result
        else:
          return list()

      if comment_id:
        comment = self.event_controller.get_comment_by_uuid(comment_id)
      else:
        raise PathParsingException(u'comment cannot be called without an ID')
      if method == 'GET':
        return comment.to_dict()
      elif method == 'PUT':
        comment = self.updater.update(comment, json, cache_object)
        self.event_controller.update_comment(comment, cache_object)
        return comment.to_dict()
      elif method == 'DELETE':
        self.event_controller.remove_comment(comment, cache_object)
        return 'Deleted comment'
      else:
        raise RestHandlerException(u'Invalid request')

  def __process_event(self, method, event, json, cache_object):
    if method == 'GET':
      return self.__return_event(event, cache_object)
    elif method == 'POST':
      # this cannot happen here
      raise RestHandlerException(u'Invalid request')
    elif method == 'PUT':
      self.check_if_is_modifiable(event)
      # check if validated / shared as only the owner can do this
      self.check_if_user_can_set_validate_or_shared(event, event, cache_object, json)
      self.updater.update(event, json, cache_object)
      self.event_controller.update_event(event, cache_object, True, True)
      return self.__return_event(event, cache_object)
    elif method == 'DELETE':
      self.check_if_is_deletable(event)
      self.event_controller.remove_event(event, cache_object)
      return 'Deleted event'

  def __process_indicator(self, method, event, requested_object, json, cache_object):
    if method == 'GET':
      observable_id = requested_object['object_uuid']
      if observable_id:
        raise RestHandlerException('Not implemented')
      else:
        result = event.attributelist_to_dict('indicators', cache_object)
        if result:
          return result
        else:
          # generate indicators
          indicators = self.indicator_controller.get_generic_indicators(event, cache_object)
          result = list()
          for indicator in indicators:
            if self.permission_controller.is_instance_viewable(indicator, cache_object):
              result.append(indicator.to_dict(cache_object))
          return result
    else:
      raise RestHandlerException('Not implemented')

  def __process_observable(self, method, event, requested_object, json, cache_object):
    if method == 'POST':
      cache_object_copy = cache_object.make_copy()
      observable = self.assembler.assemble(json, Observable, event, cache_object)
      self.observable_controller.insert_observable(observable, cache_object, True)
      cache_object_copy.inflated = True
      return observable.to_dict(cache_object_copy)
    else:
        uuid = requested_object['object_uuid']
        if uuid:
          observable = self.observable_controller.get_observable_by_uuid(uuid)
          self.check_if_instance_is_viewable(observable, cache_object)
        if method == 'GET':
          if uuid:
            return observable.to_dict(cache_object)
          else:
            # return all observables from the event
            result = event.attributelist_to_dict('observables', cache_object)
            if result is None:
              return list()
            else:
              return result
        if uuid is None:
          raise PathParsingException(u'observale cannot be called without an ID')
        if method == 'PUT':
          self.check_if_is_modifiable(event)
          self.check_allowed_set_validate_or_shared(event, observable, cache_object, json)
          self.updater.update(observable, json, cache_object)
          self.observable_controller.update_observable(observable, cache_object, True)
          return observable.to_dict(cache_object)
        elif method == 'DELETE':
          self.check_if_is_deletable(event)
          # TODO: unify the following
          if observable.observable_composition:
            self.check_if_instance_is_viewable(observable.observable_composition, cache_object)
            self.observable_controller.remove_observable_composition(observable.observable_composition, cache_object, True)
          self.check_if_instance_is_viewable(observable, cache_object)
          self.observable_controller.remove_observable(observable, cache_object, True)
          return 'Deleted observable'

  def __return_event(self, event, cache_object):
    # Add additional permissions for the user

    result = event.to_dict(cache_object)
    result['userpermissions'] = cache_object.event_permissions.to_dict(cache_object)
    result['userpermissions']['owner'] = cache_object.event_owner
    return result

  def __process_event_validate(self, method, event, requested_object, json, cache_object):
    if method != 'PUT':
      raise RestHandlerException('Operation not supported')
    self.check_if_instance_owner(event, cache_object)
    self.event_controller.validate_event(event, cache_object)
    return 'Event validated'

  def __process_event_group(self, method, event, requested_object, json, cache_object):
    self.check_if_can_change_groups(event)
    if method == 'GET':
        uuid = requested_object['object_uuid']
        if uuid:
          event_permission = self.event_controller.get_event_permission_by_uuid(uuid)
          return event_permission.to_dict(cache_object)
        else:
          result = event.attributelist_to_dict('groups', cache_object)
          if result:
            return result
          else:
            return list()
    elif method == 'POST':
      # get group
      event_group_permission = self.assembler.assemble(json, EventGroupPermission, event, cache_object)
      self.event_controller.insert_event_group_permission(event_group_permission, cache_object, True)
      return event_group_permission.to_dict(cache_object)
    elif method == 'PUT':
      uuid = requested_object.get('object_uuid', None)
      if uuid:
        event_group_permission = self.event_controller.get_event_permission_by_uuid(uuid)
        self.updater.update(event_group_permission, json, cache_object)
        self.observable_controller.update_observable(event_group_permission, cache_object, True)
        return event_group_permission.to_dict(cache_object)

    elif method == 'DELETE':
      uuid = requested_object.get('object_uuid', None)
      if uuid:
        # get group
        event_group_permission = self.event_controller.get_event_group_by_uuid(uuid)

        self.event_controller.remove_group_permissions(event_group_permission, cache_object, True)
        return 'OK'
      else:
        raise RestHandlerException(u'Cannot remove group as no group was provided')

    else:
      raise RestHandlerException('Operation not supported')

  def __process_event_relations(self, method, event, requested_object, json, cache_object):
    if method == 'GET':
      result = list()
      if cache_object.details:
        # return the complete with evety event attribute etc
        relations = self.relation_controller.get_relations_for_event(event)
        for relation in relations:
          rel_event = relation.rel_event
          rel_attr = relation.rel_attribute
          if self.is_instance_viewable(rel_event, cache_object) and self.is_instance_viewable(rel_attr, cache_object):
            result.append(relation.to_dict(cache_object))

        return result
      else:
        # return only the unique events
        relations = self.relation_controller.get_related_events_for_event(event)
        for relation in relations:
          rel_event = relation.rel_event
          if self.is_instance_viewable(rel_event, cache_object):
            result.append(rel_event.to_dict(cache_object))

        return result
    elif method == 'DELETE':
      self.check_if_is_deletable(event)
      uuid = requested_object.get('object_uuid', None)
      if uuid:
        # TODO delete relation
        raise RestHandlerException('Operation not implemented')
      else:
        raise RestHandlerException(u'Cannot remove relations as no relation id was provided')

    else:
      raise RestHandlerException('Operation not supported')

  def __process_event_report(self, method, event, requested_object, json, cache_object):

    if method == 'GET':
      uuid = requested_object['object_uuid']
      if uuid:
        # return the given observable
        # TODO: Check if observable belongs to event
        report = self.report_controller.get_report_by_uuid(uuid)
        if self.is_instance_viewable(report, cache_object):
          return report.to_dict(cache_object)
        else:
          raise ControllerNothingFoundException(u'Cannot find report with uuid {0}'.format(uuid))
      else:
        # return all observables from the event
        cache_object.inflated = True
        result = event.attributelist_to_dict('reports', cache_object)
        if result is None:
          return list()
        else:
          return result
    if method == 'POST':
      self.check_if_is_modifiable(event)
      report = self.assembler.assemble(json, Report, event, cache_object)
      self.report_controller.insert_report(report, cache_object)
      return report.to_dict(cache_object)
    else:
      raise RestHandlerException('Operation not supported')
    return list()

  def __publish_event(self, method, event, requested_object, json, cache_object):
    self.check_if_instance_owner(event, cache_object)
    if method == 'POST':
      self.event_controller.publish_event(event, cache_object)

      type_ = ProcessType.PUBLISH
      if event.last_publish_date:
        type_ = ProcessType.PUBLISH_UPDATE
      servers = self.server_controller.get_all_push_servers()
      for server in servers:
        if self.is_event_viewable(event, server.user):
          self.process_controller.create_new_process(type_, event.uuid, cache_object.user, server, False)
      # add also mail
      self.process_controller.create_new_process(type_, event.uuid, cache_object.user, None, False)
      self.process_controller.process_broker.do_commit(True)

      return 'Published event.'
    else:
      raise RestHandlerException('Method is undefined.')
