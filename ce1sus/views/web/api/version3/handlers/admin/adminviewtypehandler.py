# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 7, 2014
"""
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.db.classes.types import AttributeType, AttributeViewType
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttribueViewTypeHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attribute_definition_controller = AttributeDefinitionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require(privileged())
  def view_types(self, **args):
    try:
      method = args.get('method')
      json = args.get('json')
      path = args.get('path')
      details = self.get_detail_value(args)
      if method == 'GET':
        if len(path) > 0:
          uuid = path.pop(0)
          type_ = self.attribute_definition_controller.get_view_type_by_id(uuid)
          return type_.to_dict(complete=details)
        else:
          view_types = self.attribute_definition_controller.get_all_view_types()
          result = list()
          for view_type in view_types:
            result.append(view_type.to_dict(complete=details))
          return result
      elif method == 'POST':
        if len(path) > 0:
          raise RestHandlerException(u'No post definied on the given path')
        else:
          # Add new type
          type_ = AttributeViewType()
          type_.populate(json)
          # set the new checksum
          self.attribute_definition_controller.insert_view_type(type_)
          return type_.to_dict()
      elif method == 'PUT':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          type_ = self.attribute_definition_controller.get_view_type_by_id(uuid)
          type_.populate(json)
          self.attribute_definition_controller.update_view_type(type_)
          return type_.to_dict()
        else:
          raise RestHandlerException(u'Cannot update user as no identifier was given')
      elif method == 'DELETE':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          self.attribute_definition_controller.remove_view_type_by_id(uuid)
          return 'OK'
        else:
          raise RestHandlerException(u'Cannot delete user as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
