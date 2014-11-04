# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
import re

from ce1sus.controllers.admin.group import GroupController
from ce1sus.controllers.base import ControllerException
from ce1sus.db.classes.group import Group
from ce1sus.helpers.common.hash import hashSHA1
from ce1sus.helpers.pluginfunctions import is_plugin_available, get_plugin_function
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminGroupHandler(RestBaseHandler):

  PASSWORD_MASK = '*******************'

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.group_controller = GroupController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'POST', 'PUT', 'DELETE'])
  @require(privileged())
  def group(self, **args):
    try:
      method = args.get('method')
      path = args.get('path')
      headers = args.get('headers')
      details = headers.get('Complete', 'false')
      json = args.get('json')
      if method == 'GET':

        if len(path) > 0:
          # if there is a uuid as next parameter then return single group
          uuid = path.pop(0)
          # TODO: add inflate
          group = self.group_controller.get_group_by_id(uuid)

          if details == 'true':
            details = True
          else:
            details = False

          if len(path) > 0:
            # check if the next path
            children = path.pop(0)
            if children == 'children':
              # return the children of the group

              result = list()
              for child in group.children:
                result.append(child.to_dict(complete=details))
              return result

          return group.to_dict(complete=details)
        else:
          # else return all
          groups = self.group_controller.get_all_groups()
          result = list()
          for group in groups:
            if details == 'true':
              result.append(group.to_dict())
            else:
              result.append(group.to_dict(complete=False))
          return result

      elif method == 'POST':
        # Add new group
        group = Group()
        group.populate(json)
        self.group_controller.insert_group(group)
        return group.to_dict()
      elif method == 'PUT':
        # update group
        if len(path) > 0:
          # if there is a uuid as next parameter then return single group
          uuid = path.pop(0)
          group = self.group_controller.get_group_by_id(uuid)
          group.populate(json)
          self.group_controller.update_group(group)
          return group.to_dict()
        else:
          raise RestHandlerException(u'Cannot update group as no identifier was given')

      elif method == 'DELETE':
        # Remove group
        if len(path) > 0:
          # if there is a uuid as next parameter then return single group
          uuid = path.pop(0)
          self.group_controller.remove_group_by_id(uuid)
          return 'Deleted group'
        else:
          raise RestHandlerException(u'Cannot delete group as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerException as error:
      raise RestHandlerException(error)


