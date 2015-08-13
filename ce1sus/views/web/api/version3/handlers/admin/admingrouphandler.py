# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
from ce1sus.controllers.admin.group import GroupController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.internal.usrmgt.group import Group
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminGroupHandler(RestBaseHandler):

  def __init__(self, config):
    super(RestBaseHandler, self).__init__(config)
    self.group_controller = self.controller_factory(GroupController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'POST', 'PUT', 'DELETE'])
  @require()
  def group(self, **args):
    try:
      method = args.get('method')
      path = args.get('path')
      json = args.get('json')
      cache_object = self.get_cache_object(args)
      if method == 'GET':

        if len(path) > 0:
                    # if there is a uuid as next parameter then return single group
          uuid = path.pop(0)

          group = self.group_controller.get_group_by_uuid(uuid)

          if len(path) > 0:
                        # check if the next path
            children = path.pop(0)
            if children == 'children':
                            # return the children of the group

              result = list()
              for child in group.children:
                result.append(child.to_dict(cache_object))
              return result

          return group.to_dict(cache_object)
        else:
          # else return all
          groups = self.group_controller.get_all_groups()
          result = list()
          for group in groups:
            result.append(group.to_dict(cache_object))
          return result

      elif method == 'POST':
        self.check_if_admin()
        if len(path) > 0:
          uuid = path.pop(0)
          group = self.group_controller.get_group_by_uuid(uuid)
          if len(path) > 0:
            type_ = path.pop(0)
            if type_ == 'children':
            # get the object definition
              if isinstance(json, list):
                # TODO: add support for lists
                raise RestHandlerException(u'POST of group children does not support lists')
              uuid = json.get('identifier', None)
              if uuid:
                child = self.group_controller.get_group_by_uuid(uuid)
                group.children.append(child)
                self.group_controller.update_group(group)
                return 'OK'
              else:
                raise RestHandlerException(u'No id was specified in the json post')
            else:
              raise RestHandlerException(u'"{0}" is not supported'.format(type_))
          else:
            raise RestHandlerException(u'If an id was specified you also must specify on which type it is associated')
        else:
          # Add new group
          group = self.assembler.assemble(json, Group, None, cache_object)
          self.group_controller.insert_group(group)
          return group.to_dict(cache_object)
      elif method == 'PUT':
        self.check_if_admin()
        # update group
        if len(path) > 0:
          # if there is a uuid as next parameter then return single group
          uuid = path.pop(0)
          group = self.group_controller.get_group_by_uuid(uuid)
          self.updater.update(group, json, cache_object)
          self.group_controller.update_group(group)
          return group.to_dict(cache_object)
        else:
          raise RestHandlerException(u'Cannot update group as no identifier was given')

      elif method == 'DELETE':
        self.check_if_admin()
        # Remove group
        if len(path) > 0:
          # if there is a uuid as next parameter then return single group
          uuid = path.pop(0)
          if len(path) > 0:
            type_ = path.pop(0)
            if len(path) > 0:
              group = self.group_controller.get_group_by_uuid(uuid)
              uuid = path.pop(0)
              child = self.group_controller.get_group_by_uuid(uuid)
              group.children.remove(child)
              self.group_controller.update_group(group)
            else:
              raise RestHandlerException(u'If an id was specified you also must specify on which type it is associated')
          else:
            self.group_controller.remove_group_by_uuid(uuid)
          return 'OK'
        else:
          raise RestHandlerException(u'Cannot delete group as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
