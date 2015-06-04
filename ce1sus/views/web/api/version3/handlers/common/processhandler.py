# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 8, 2014
"""

from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.controllers.common.process import ProcessController
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerNotFoundException, RestHandlerException
from ce1sus.views.web.common.decorators import privileged
from ce1sus.handlers.base import HandlerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ProcessHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.process_controller = ProcessController(config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def processes(self, **args):
    try:
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)

      if len(path) > 0:
                # if there is a uuid as next parameter then return single user
        uuid = path.pop(0)
        process = self.process_controller.get_process_item_by_uuid(uuid)
        return process.to_dict(details, inflated)
      else:
        processes = self.process_controller.get_all_process_items()
        result = list()
        for process in processes:
          result.append(process.to_dict(details, inflated))
        return result
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  @rest_method()
  @methods(allowed=['GET'])
  @require(privileged())
  def reschedule(self, **args):
    try:
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      if len(path) > 0:
        uuid = path.pop(0)
        item = self.process_controller.get_process_item_by_uuid(uuid)
        user = self.get_user()

        self.process_controller.process_restart(item, user)
        return item.to_dict(details, inflated)
      else:
        raise RestHandlerException('No identifier provided')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  @rest_method()
  @methods(allowed=['GET'])
  @require(privileged())
  def cancel(self, **args):
    try:
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      if len(path) > 0:
        uuid = path.pop(0)
        item = self.process_controller.get_process_item_by_uuid(uuid)
        user = self.get_user()

        self.process_controller.process_cancelled(item, user)
        return item.to_dict(details, inflated)
      else:
        raise RestHandlerException('No identifier provided')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)

  @rest_method()
  @methods(allowed=['GET'])
  @require(privileged())
  def remove(self, **args):
    try:
      path = args.get('path')
      if len(path) > 0:
        uuid = path.pop(0)
        item = self.process_controller.get_process_item_by_uuid(uuid)
        user = self.get_user()

        self.process_controller.process_remove(item, user)
        return 'OK'
      else:
        raise RestHandlerException('No identifier provided')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
