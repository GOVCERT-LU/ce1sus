# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 9, 2015
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.events.reports import ReportController
from ce1sus.db.classes.internal.common import ValueException
from ce1sus.db.classes.internal.report import Report, Reference
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
        self.set_event_properties_cache_object(cache_object, event)
        self.check_if_instance_is_viewable(event, cache_object)
        self.check_if_instance_is_viewable(report, cache_object)

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
          self.check_if_is_modifiable(event)
          self.check_allowed_set_validate_or_shared(event, report, cache_object, json)
          self.updater.update(report, json, cache_object)
          self.report_controller.update_report(report, cache_object, True)
          return report.to_dict(cache_object)
        elif method == 'DELETE':
          self.check_if_is_deletable(event)
          self.report_controller.remove_report(report, cache_object, True)
          return 'Deleted report'
    except ValueException as error:
      raise RestHandlerException(error)

  def __process_child_report(self, method, event, report, requested_object, json, cache_object):
    if method == 'POST':
      child_obj = self.assembler.assemble(json, Report, event, cache_object)
      # TODO place this in a controller or so
      child_obj.parent_report_id = report.identifier

      self.report_controller.insert_report(child_obj, cache_object, False)
      return child_obj.to_dict(cache_object)
    else:
      raise RestHandlerException('Please use report/{uuid}/ instead')

  def __process_reference(self, method, event, report, requested_object, json, cache_object):
    try:
      if method == 'POST':

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
        if uuid:
          reference = self.report_controller.get_reference_by_uuid(uuid)
          self.check_if_instance_is_viewable(reference, cache_object)
          
        if method == 'GET':
          if uuid:
            return reference.to_dict(cache_object)
          else:
            result = list()
            for reference in report.references:
              if self.is_item_viewable(event, reference):
                result.append(reference.to_dict(cache_object))
            return result
        else:
          if method == 'PUT':
            self.check_if_is_modifiable(event)
            self.check_allowed_set_validate_or_shared(event, reference, cache_object, json)
            self.updater.update(reference, json, cache_object)
            self.report_controller.update_reference(reference, cache_object)
            return reference.to_dict(cache_object)
          elif method == 'DELETE':
            self.check_if_is_deletable(event)
            self.check_item_is_viewable(event, reference)
            self.report_controller.remove_reference(reference, cache_object, True)
            return 'Deleted object'

    except ValueException as error:
      raise RestHandlerException(error)
