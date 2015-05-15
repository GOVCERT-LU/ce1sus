# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 9, 2015
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException, NotImplementedException
from ce1sus.controllers.events.reports import ReportController
from ce1sus.db.classes.common import ValueException
from ce1sus.handlers.base import HandlerException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException, RestHandlerNotFoundException, PathParsingException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ReportHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.report_controller = self.controller_factory(ReportController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def report(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      headers = args.get('headers')
      # get the event
      report_id = requested_object.get('event_id')
      if report_id:
        report = self.report_controller.get_report_by_uuid(report_id)
        event = report.event
        self.check_if_event_is_viewable(event)
        if requested_object['object_type'] is None:
          # return the report
          return self.__process_report(method, event, report, details, inflated, json, headers)
        elif requested_object['object_type'] == 'report':
          return self.__process_child_report(method, event, report, requested_object, details, inflated, json, headers)
        elif requested_object['object_type'] == 'reference':
          return self.__process_reference(method, event, report, requested_object, details, inflated, json, headers)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Report cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_report(self, method, event, report, details, inflated, json, headers):
    try:
      user = self.get_user()
      if method == 'POST':
        raise RestHandlerException('Please use event/{uuid}/report instead')
      else:
        event_permissions = self.get_event_user_permissions(event, user)
        if method == 'GET':
          self.check_item_is_viewable(event, report)
          return report.to_dict(details, inflated, event_permissions, user)
        elif method == 'PUT':
          old_report = report
          self.check_if_event_is_modifiable(event)
          self.check_if_user_can_set_validate_or_shared(event, old_report, user, json)
          # check if there was not a parent set
          parent_id = json.get('parent_report_id', None)
          # TODO Review the relations as they have to be removed at some point if they were existing
          if parent_id:
            # get related object
            related_report = self.observable_controller.get_related_report_by_child(report)
            # check if parent has changed
            if related_report.parent_report_id != parent_id:
              # unbind the earlier relation
              related_report.parent_report_id = parent_id
              self.report_controller.update_related_report(related_report, user, False)
          report = self.assembler.update_report(report, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))
          self.report_controller.update_report(report, user, True)
          return report.to_dict(details, inflated, event_permissions, user)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          self.report_controller.remove_report(report, user, True)
          return 'Deleted report'
    except ValueException as error:
      raise RestHandlerException(error)

  def __process_child_report(self, method, event, report, requested_object, details, inflated, json, headers):
    user = self.get_user()
    if method == 'POST':
      self.check_if_user_can_add(event)
      child_obj = self.assembler.assemble_child_report(report, event, json, user, self.is_event_owner(event, user), self.is_rest_insert(headers))

      self.report_controller.insert_report(child_obj, user, False)
      event_permissions = self.get_event_user_permissions(event, user)
      return child_obj.to_dict(details, inflated, event_permissions, user)
    else:
      raise RestHandlerException('Please use report/{uuid}/ instead')

  def __get_handler(self, definition):
    handler_instance = definition.handler
    handler_instance.reference_definitions[definition.chksum] = definition

    # Check if the handler requires additional attribute definitions
    additional_ref_defs_chksums = handler_instance.get_additinal_reference_chksums()

    if additional_ref_defs_chksums:
      additional_ref_defs_chksums = self.report_controller.get_defintion_by_chksums(additional_ref_defs_chksums)
      for additional_ref_definition in additional_ref_defs_chksums:
        handler_instance.reference_definitions[additional_ref_definition.chksum] = additional_ref_definition

    handler_instance.user = self.get_user()
    return handler_instance

  def __process_reference(self, method, event, report, requested_object, details, inflated, json, headers):
    try:
      user = self.get_user()
      if method == 'POST':
        self.check_if_user_can_add(event)
        # Get needed handler
        definition = self.report_controller.get_reference_definitions_by_uuid(json.get('definition_id', None))
        handler_instance = self.__get_handler(definition)
        handler_instance.is_rest_insert = self.is_rest_insert(headers)
        handler_instance.is_owner = self.is_event_owner(event, user)
        # Ask handler to process the json for the new attributes
        reference, additional_references, related_reports = handler_instance.insert(report, user, json)
        # Check if not elements were attached to the object
        # TODO: find a way to check if the object has been changed
        # TODO also check if there are no children attached
        if True:
          self.report_controller.insert_reference(reference, additional_references, user, False, self.is_event_owner(event, user))
          if related_reports:
            raise NotImplementedException('Related reports returned for handler {0} but the processing is not'.format(definition.attribute_handler.classname))
          self.report_controller.insert_handler_reports(related_reports, user, True, self.is_event_owner(event, user))
        else:
          raise RestHandlerException('The object has been modified by the handler {0} this cannot be'.format(definition.attribute_handler.classname))

        # Return the generated references as json
        result_references = list()
        result_references.append(reference.to_dict(details, inflated))
        if additional_references:
          for additional_reference in additional_references:
            result_references.append(additional_reference.to_dict(details, inflated))

        result_reports = list()
        if related_reports:
          for related_object in related_reports:
            result_reports.append(related_object.to_dict(details, inflated))

        return {'references': result_references, 'related_reports': result_reports}

      else:
        uuid = requested_object['object_uuid']
        if method == 'GET':
          if uuid:
            reference = self.report_controller.get_reference_by_uuid(uuid)
            self.check_item_is_viewable(event, reference)
            return reference.to_dict(details, inflated)
          else:
            result = list()
            for reference in report.references:
              if self.is_item_viewable(event, reference):
                result.append(reference.to_dict(details, inflated))
            return result
        else:
          reference = self.report_controller.get_reference_by_uuid(uuid)
          if method == 'PUT':
            old_ref = reference
            self.check_if_event_is_modifiable(event)
            self.check_item_is_viewable(event, reference)
            definition_uuid = json.get('definition_id', None)
            if definition_uuid:
              # check if it still is the same
              if not reference.definition.uuid == definition_uuid:
                raise HandlerException('It is not possible to change the definition of references')

            handler_instance = self.__get_handler(reference.definition)
            handler_instance.is_rest_insert = self.is_rest_insert(headers)
            handler_instance.is_owner = self.is_event_owner(event, user)

            self.check_if_user_can_set_validate_or_shared(event, old_ref, user, json)

            # Ask handler to process the json for the new attributes
            reference = handler_instance.update(reference, user, json)

            self.logger.info(u'User {0} changed reference {1} from {2} to {3}'.format(user.username, old_ref.identifier, old_ref.value, reference.value))

            # TODO: check if there are no children attached
            self.report_controller.update_reference(reference, user, True)

            return reference.to_dict(details, inflated)
          elif method == 'DELETE':
            self.check_if_event_is_deletable(event)
            self.check_item_is_viewable(event, reference)
            self.report_controller.remove_reference(reference, user, True)
            return 'Deleted object'

    except ValueException as error:
      raise RestHandlerException(error)
