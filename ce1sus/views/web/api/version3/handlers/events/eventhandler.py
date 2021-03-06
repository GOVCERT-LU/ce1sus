# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
import cherrypy

from ce1sus.common.checks import is_object_viewable
from ce1sus.controllers.admin.syncserver import SyncServerController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.controllers.common.process import ProcessController
from ce1sus.controllers.events.indicatorcontroller import IndicatorController
from ce1sus.controllers.events.observable import ObservableController
from ce1sus.controllers.events.relations import RelationController
from ce1sus.controllers.events.reports import ReportController
from ce1sus.db.classes.event import EventGroupPermission
from ce1sus.db.classes.processitem import ProcessType
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException, RestHandlerNotFoundException, PathParsingException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class EventHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
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
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      headers = args.get('headers')
      # get the event
      event_id = requested_object.get('event_id')
      if event_id:
        event = self.event_controller.get_event_by_uuid(event_id)
        # check if event is viewable by the current user
        self.check_if_event_is_viewable(event)

        if requested_object['object_type'] is None:
                    # return the event
          return self.__process_event(method, event, details, inflated, json, headers)
        elif requested_object['object_type'] == 'observable':
          return self.__process_observable(method, event, requested_object, details, inflated, json, headers)
        elif requested_object['object_type'] == 'indicator':
          return self.__process_indicator(method, event, requested_object, details, inflated, json, headers)
        elif requested_object['object_type'] == 'observable_composition':
          return self.__process_composed_observable(method, event, requested_object, details, inflated, json)
        elif requested_object['object_type'] == 'changegroup':
          self.check_if_admin()
          return self.__change_event_group(method, event, json)
        elif requested_object['object_type'] == 'comment':
          return self.__process_commment(method, event, requested_object, details, inflated, json, headers)
        elif requested_object['object_type'] == 'publish':
          return self.__publish_event(method, event, requested_object, details, inflated, json, headers)
        elif requested_object['object_type'] == 'validate':
          return self.__process_event_validate(method, event, requested_object, details, inflated, json)
        elif requested_object['object_type'] == 'group':
          return self.__process_event_group(method, event, requested_object, details, inflated, json)
        elif requested_object['object_type'] == 'relations':
          return self.__process_event_relations(method, event, requested_object, details, inflated, json)
        elif requested_object['object_type'] == 'report':
          return self.__process_event_report(method, event, requested_object, details, inflated, json, headers)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        # This can only happen when a new event is inserted
        if method == 'POST':
          # populate event
          user = self.get_user()
          event = self.assembler.assemble_event(json, user, True, self.is_rest_insert(headers))
          self.event_controller.insert_event(user, event, True, True)

          return self.__return_event(event, details, inflated)
        else:
          raise RestHandlerException(u'Invalid request - Event cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __change_event_group(self, method, event, json):
    if method == 'PUT':
      if self.is_user_priviledged(self.get_user()):
        group_id = json.get('identifier', None)
        self.event_controller.change_owner(event, group_id, self.get_user())

        return 'OK'
      else:
        raise cherrypy.HTTPError(403, 'No allowed')
    else:
      raise RestHandlerException(u'Invalid request')

  def __process_commment(self, method, event, requested_object, details, inflated, json, headers):
    self.check_if_owner(event)
    user = self.get_user()
    if method == 'POST':
      comment = self.assembler.assemble_comment(event, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
      self.event_controller.insert_comment(user, comment)
      return comment.to_dict(details, inflated)
    else:
      comment_id = requested_object['object_uuid']
      if comment_id:
        comment = self.event_controller.get_comment_by_uuid(comment_id)
      else:
        raise PathParsingException(u'comment cannot be called without an ID')
      if method == 'GET':
        return comment.to_dict(details, inflated)
      elif method == 'PUT':
        self.check_if_event_is_modifiable(event)
        comment = self.assembler.update_comment(comment, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
        self.event_controller.update_comment(user, comment)
        return comment.to_dict(details, inflated)
      elif method == 'DELETE':
        self.check_if_event_is_deletable(event)
        self.event_controller.remove_comment(user, comment)
        return 'Deleted comment'
      else:
        raise RestHandlerException(u'Invalid request')

  def __process_event(self, method, event, details, inflated, json, headers):
    if method == 'GET':
      return self.__return_event(event, details, inflated)
    elif method == 'POST':
      # this cannot happen here
      raise RestHandlerException(u'Invalid request')
    elif method == 'PUT':
      old_event = event
      user = self.get_user()
      self.check_if_event_is_modifiable(event)
      # check if validated / shared as only the owner can do this
      self.check_if_user_can_set_validate_or_shared(event, old_event, user, json)
      event = self.assembler.update_event(event, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))

      self.event_controller.update_event(user, event, True, True)
      return self.__return_event(event, details, inflated)
    elif method == 'DELETE':
      self.check_if_event_is_deletable(event)
      self.event_controller.remove_event(self.get_user(), event)
      return 'Deleted event'

  def __process_indicator(self, method, event, requested_object, details, inflated, json, headers):
    user = self.get_user()

    if method == 'GET':
      self.check_if_event_is_viewable(event)
      event_permission = self.get_event_user_permissions(event, user)
      observable_id = requested_object['object_uuid']
      if observable_id:
        raise RestHandlerException('Not implemented')
      else:
        result = list()
        for indicator in event.get_indicators_for_permissions(event_permission, user):
          if self.is_item_viewable(event, indicator):
            result.append(indicator.to_dict(details, inflated, event_permission, user))
        if result:
          return result
        else:
          # generate indicators
          indicators = self.indicator_controller.get_generic_indicators(event, user)
          result = list()
          for indicator in indicators:
            if self.is_item_viewable(event, indicator):
              result.append(indicator.to_dict(details, inflated, event_permission, user))
          return result
    else:
      raise RestHandlerException('Not implemented')

  def __process_observable(self, method, event, requested_object, details, inflated, json, headers):
    user = self.get_user()
    event_permissions = self.get_event_user_permissions(event, user)
    if method == 'POST':
      self.check_if_user_can_add(event)
      observable = self.assembler.assemble_observable(event, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
      self.observable_controller.insert_observable(observable, user, True)
      return observable.to_dict(details, inflated, event_permissions, user)
    else:
      if method == 'GET':
        self.check_if_event_is_viewable(event)
        return self.__process_observable_get(event, requested_object, details, inflated)
      else:
        observable_id = requested_object['object_uuid']
        if observable_id:
          observable = self.observable_controller.get_observable_by_uuid(observable_id)
          self.check_item_is_viewable(event, observable)
        else:
          raise PathParsingException(u'observale cannot be called without an ID')
        if method == 'PUT':
          old_observable = observable
          self.check_if_event_is_modifiable(event)

          self.check_if_user_can_set_validate_or_shared(event, old_observable, user, json)

          observable = self.assembler.update_observable(observable, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
          self.observable_controller.update_observable(observable, user, True)
          return observable.to_dict(details, inflated, event_permissions, user)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          if observable.observable_composition:
            self.observable_controller.remove_observable_composition(observable.observable_composition, user, True)
          self.observable_controller.remove_observable(observable, user, True)
          return 'Deleted observable'

  def __process_observable_get(self, event, requested_object, details, inflated):
    user = self.get_user()

    try:
      event_permission = self.get_event_user_permissions(event, user)
      uuid = requested_object['object_uuid']
      if uuid:
        # return the given observable
        # TODO: Check if observable belongs to event
        observable = self.observable_controller.get_observable_by_uuid(uuid)
        self.check_item_is_viewable(event, observable)
        if is_object_viewable(observable, event_permission, user):
          return observable.to_dict(details, inflated, event_permission, user)
        else:
          raise ControllerNothingFoundException(u'Cannot find observable with uuid {0}'.format(uuid))

      else:
        # return all observables from the event
        result = list()
        for observable in event.get_observables_for_permissions(event_permission, user):
          if self.is_item_viewable(event, observable):
            result.append(observable.to_dict(details, inflated, event_permission, user))

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
      self.check_if_event_is_deletable(event)
      self.event_controller.remove_event(self.get_user(), event)

  def __process_composed_observable_get(self, requested_object, details, inflated):
    try:
      uuid = requested_object['object_uuid']
      if uuid:
        composed_observable = self.observable_controller.get_composed_observable_by_uuid(uuid)
        return composed_observable.to_dict(details, inflated)
      else:
        raise PathParsingException(u'observable_composition cannot be called without an ID')
    except ControllerException as error:
      raise RestHandlerException(error)

  def __return_event(self, event, details, inflated):
    # Add additional permissions for the user
    user = self.get_user()
    event_permission = self.get_event_user_permissions(event, user)
    owner = self.is_event_owner(event, user)
    result = event.to_dict(details, inflated, event_permission, user)
    result['userpermissions'] = event_permission.to_dict()
    result['userpermissions']['owner'] = owner
    return result

  def __process_event_validate(self, method, event, requested_object, details, inflated, json):
    if method != 'PUT':
      raise RestHandlerException('Operation not supported')
    self.check_if_admin_validate()
    self.event_controller.validate_event(event, self.get_user())
    return 'Event validated'

  def __process_event_group(self, method, event, requested_object, details, inflated, json):
    if method == 'POST':
      self.check_if_event_group_can_change(event)
      # get group
      group = json.get('group', None)
      if group:
        uuid = group.get('identifier')
        if uuid:
          # get group
          group = self.event_controller.get_group_by_uuid(uuid)
          # append
          event_group_permission = EventGroupPermission()
          event_group_permission.event_id = event.identifier
          event_group_permission.group = group
          permissions = json.get('permissions', None)
          if permissions:
            event_group_permission.permissions.populate(permissions)
          else:
            # use defaults
            event_group_permission.dbcode = group.default_dbcode

          self.event_controller.insert_event_group_permission(self.get_user(), event_group_permission, True)
          return event_group_permission.to_dict()
        else:
          raise RestHandlerException(u'Cannot add group as no group was provided')
      else:
        raise RestHandlerException(u'Cannot add group as no group was provided')

    elif method == 'PUT':
      self.check_if_event_is_modifiable(event)
      uuid = requested_object.get('object_uuid', None)
      if uuid:
        # get permissions

        json_permissions = json.get('permissions', None)
        if json_permissions:
          event_group = self.event_controller.get_event_group_by_uuid(uuid)
          event_group.permissions.populate(json_permissions)
          self.event_controller.update_event_group_permissions(self.get_user(), event_group, True)
          return event_group.to_dict()
        else:
          raise RestHandlerException(u'Cannot update group permissions for group {1} on event {0} as uuid was specified'.format(event.identifer, uuid))

      else:
        raise RestHandlerException(u'Cannot update group permissions for event {0} as uuid was specified'.format(event.identifer))

    elif method == 'DELETE':
      self.check_if_event_group_can_change(event)
      uuid = requested_object.get('object_uuid', None)
      if uuid:
        # get group
        event_group_permission = self.event_controller.get_event_group_by_uuid(uuid)

        self.event_controller.remove_group_permissions(self.get_user(), event_group_permission, True)
        return 'OK'
      else:
        raise RestHandlerException(u'Cannot remove group as no group was provided')

    else:
      raise RestHandlerException('Operation not supported')

  def __process_event_relations(self, method, event, requested_object, details, inflated, json):
    if method == 'GET':
      result = list()
      if details:
        # return the complete with evety event attribute etc
        relations = self.relation_controller.get_relations_for_event(event)
        for relation in relations:
          rel_event = relation.rel_event
          rel_attr = relation.rel_attribute
          if self.is_event_viewable(rel_event) and self.is_item_viewable(rel_event, rel_attr):
            event_permissions = self.get_event_user_permissions(rel_event, self.get_user())
            result.append(relation.to_dict(details, inflated, event_permissions, self.get_user()))

        return result
      else:
        # return only the unique events
        relations = self.relation_controller.get_related_events_for_event(event)
        for relation in relations:
          rel_event = relation.rel_event
          if self.is_event_viewable(rel_event):
            event_permissions = self.get_event_user_permissions(rel_event, self.get_user())
            result.append(rel_event.to_dict(details, inflated, event_permissions, self.get_user()))

        return result
    elif method == 'DELETE':
      uuid = requested_object.get('object_uuid', None)
      if uuid:
        # TODO delete relation
        raise RestHandlerException('Operation not implemented')
      else:
        raise RestHandlerException(u'Cannot remove relations as no relation id was provided')

    else:
      raise RestHandlerException('Operation not supported')

  def __process_event_report(self, method, event, requested_object, details, inflated, json, headers):

    user = self.get_user()
    if method == 'GET':
      event_permission = self.get_event_user_permissions(event, user)
      uuid = requested_object['object_uuid']
      if uuid:
        # return the given observable
        # TODO: Check if observable belongs to event
        report = self.report_controller.get_report_by_uuid(uuid)
        self.check_item_is_viewable(event, report)
        if is_object_viewable(report, event_permission):
          return report.to_dict(details, inflated, event_permission, user)
        else:
          raise ControllerNothingFoundException(u'Cannot find observable with uuid {0}'.format(uuid))

      else:
        # return all observables from the event
        result = list()
        for report in event.get_reports_for_permissions(event_permission, user):
          if self.is_item_viewable(event, report):
            result.append(report.to_dict(details, inflated, event_permission, user))
        return result
    if method == 'POST':
      event_permission = self.get_event_user_permissions(event, user)
      self.check_if_user_can_add(event)
      report = self.assembler.assemble_report(event, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))

      self.report_controller.insert_report(report, user)
      return report.to_dict(details, inflated, event_permission, user)
    else:
      raise RestHandlerException('Operation not supported')
    return list()

  def __publish_event(self, method, event, requested_object, details, inflated, json, headers):
    user = self.get_user()
    if method == 'POST':
      self.event_controller.publish_event(event, user)

      type_ = ProcessType.PUBLISH
      if event.last_publish_date:
        type_ = ProcessType.PUBLISH_UPDATE
      servers = self.server_controller.get_all_push_servers()
      for server in servers:
        if self.is_event_viewable(event, server.user):
          self.process_controller.create_new_process(type_, event.uuid, user, server, False)
      # add also mail
      self.process_controller.create_new_process(type_, event.uuid, user, None, False)
      self.process_controller.process_broker.do_commit(True)

      return 'Published event.'
    else:
      raise RestHandlerException('Method is undefined.')
