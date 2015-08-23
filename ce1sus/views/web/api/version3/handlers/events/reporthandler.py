# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 9, 2015
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.reports import ReportController
from ce1sus.db.classes.internal.common import ValueException
from ce1sus.db.classes.internal.report import Report, Reference
from ce1sus.handlers.base import HandlerException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, RestHandlerException, RestHandlerNotFoundException, PathParsingException, require


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ReportHandler(RestBaseHandler):

  def __init__(self, config):
    super(ReportHandler, self).__init__(config)
    self.report_controller = self.controller_factory(ReportController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def report(self, **args):
    try:
      method = args.get('method', None)
      path = args.get('path')
      requested_object = self.parse_path(path, method)
      json = args.get('json')
      cache_object = self.get_cache_object(args)
      # get the event
      report_id = requested_object.get('event_id')
      if report_id:
        report = self.report_controller.get_report_by_uuid(report_id)
        event = report.event
        self.check_if_event_is_viewable(event)
        self.set_event_properties_cache_object(cache_object, event)
        if requested_object['object_type'] is None:
                    # return the report
          return self.__process_report(method, event, report, json, cache_object)
        elif requested_object['object_type'] == 'report':
          return self.__process_child_report(method, event, report, requested_object, json, cache_object)
        elif requested_object['object_type'] == 'reference':
          return self.__process_reference(method, event, report, requested_object, json, cache_object)
        else:
          raise PathParsingException(u'{0} is not defined'.format(requested_object['object_type']))

      else:
        raise RestHandlerException(u'Invalid request - Report cannot be called without ID')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  def __process_report(self, method, event, report, json, cache_object):
    try:
      if method == 'POST':
        raise RestHandlerException('Please use event/{uuid}/report instead')
      else:
        if method == 'GET':
          self.check_item_is_viewable(event, report)
          return report.to_dict(cache_object)
        elif method == 'PUT':
          old_report = report
          self.check_if_event_is_modifiable(event)
          self.check_if_user_can_set_validate_or_shared(event, old_report, cache_object.user, json)
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
              self.report_controller.update_related_report(related_report, cache_object.user, False)
          report = self.updater.update(report, json, cache_object)
          self.report_controller.update_report(report, cache_object.user, True)
          return report.to_dict(cache_object)
        elif method == 'DELETE':
          self.check_if_event_is_deletable(event)
          self.report_controller.remove_report(report, cache_object.user, True)
          return 'Deleted report'
    except ValueException as error:
      raise RestHandlerException(error)

  def __process_child_report(self, method, event, report, requested_object, json, cache_object):
    if method == 'POST':
      self.check_if_user_can_add(event)
      child_obj = self.assembler.assemble(json, Report, event, cache_object)
      # TODO place this in a controller or so
      child_obj.parent_report_id = report.identifier

      self.report_controller.insert_report(child_obj, cache_object, False)
      return child_obj.to_dict(cache_object)
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

  def __process_reference(self, method, event, report, requested_object, json, cache_object):
    try:
      user = self.get_user()
      if method == 'POST':
        self.check_if_user_can_add(event)

        cache_object_copy = cache_object.make_copy()
        cache_object_copy.complete = True
        cache_object_copy.inflated = True

        # NOTE: the assembler for references assembler returns a number as the object are directly attached to the object
        returnvalues = self.assembler.assemble(json, Reference, report, cache_object)

        if isinstance(returnvalues, list):
          self.report_controller.insert_references(returnvalues, cache_object, True)
          # returns the whole report
          return returnvalues[0].report.to_dict(cache_object_copy)
        else:
          self.report_controller.update_report(returnvalues, cache_object, True)
          return returnvalues.to_dict(cache_object_copy)

      else:
        uuid = requested_object['object_uuid']
        if method == 'GET':
          if uuid:
            reference = self.report_controller.get_reference_by_uuid(uuid)
            self.check_item_is_viewable(event, reference)
            return reference.to_dict(cache_object)
          else:
            result = list()
            for reference in report.references:
              if self.is_item_viewable(event, reference):
                result.append(reference.to_dict(cache_object))
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
            handler_instance.is_rest_insert = cache_object.rest_insert
            handler_instance.is_owner = cache_object.owner

            self.check_if_user_can_set_validate_or_shared(event, old_ref, user, json)

            # Ask handler to process the json for the new attributes
            reference = handler_instance.update(reference, user, json)

            self.logger.info(u'User {0} changed reference {1} from {2} to {3}'.format(user.username, old_ref.identifier, old_ref.value, reference.value))

            # TODO: check if there are no children attached
            self.report_controller.update_reference(reference, user, True)

            return reference.to_dict(cache_object)
          elif method == 'DELETE':
            self.check_if_event_is_deletable(event)
            self.check_item_is_viewable(event, reference)
            self.report_controller.remove_reference(reference, user, True)
            return 'Deleted object'

    except ValueException as error:
      raise RestHandlerException(error)
