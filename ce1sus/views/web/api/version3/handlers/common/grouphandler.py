# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 19, 2014
"""
from ce1sus.controllers.admin.group import GroupController
from ce1sus.controllers.base import ControllerException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class GroupHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.group_controller = GroupController(config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def groups(self, **args):
    try:
      path = args.get('path')
      details = self.get_detail_value(args)
      if len(path) > 0:
        raise RestHandlerException('Path is too long')
      else:
        # else return all
        groups = self.group_controller.get_all_groups()
        result = list()
        for group in groups:
            result.append(group.to_dict(complete=details))
        return result

    except ControllerException as error:
      raise RestHandlerException(error)
