# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 24, 2014
"""
from ce1sus.controllers.admin.conditions import ConditionController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.attribute import Condition
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class ConditionHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.condition_controller = ConditionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require(privileged())
  def condition(self, **args):
    try:
      method = args.get('method')
      json = args.get('json')
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      if method == 'GET':
        if len(path) > 0:
          uuid = path.pop(0)
          condition = self.condition_controller.get_condition_by_uuid(uuid)
          return condition.to_dict(details, inflated)
        else:
          conditions = self.condition_controller.get_all_conditions()
          result = list()
          for condition in conditions:
            result.append(condition.to_dict(details, inflated))
          return result
      elif method == 'POST':
        if len(path) > 0:
          raise RestHandlerException(u'No post definied on the given path')
        else:
          # Add new type
          condition = Condition()
          condition.populate(json)
          # set the new checksum
          self.condition_controller.insert_condition(condition)
          return condition.to_dict(details, inflated)
      elif method == 'PUT':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          condition = self.condition_controller.get_condition_by_uuid(uuid)
          condition.populate(json)
          self.condition_controller.update_condition(condition)
          return condition.to_dict(details, inflated)
        else:
          raise RestHandlerException(u'Cannot update condition as no identifier was given')
      elif method == 'DELETE':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          self.condition_controller.remove_condition_by_uuid(uuid)
          return 'OK'
        else:
          raise RestHandlerException(u'Cannot delete condition as no identifier was given')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
