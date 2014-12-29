# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 7, 2014
"""
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.base import ControllerNothingFoundException, ControllerException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged
from ce1sus.db.classes.types import AttributeType


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AttribueTypeHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attribute_definition_controller = AttributeDefinitionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require(privileged())
  def types(self, **args):
    try:
      method = args.get('method')
      json = args.get('json')
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      if method == 'GET':
        if len(path) > 0:
          uuid = path.pop(0)
          type_ = self.attribute_definition_controller.get_type_by_id(uuid)
          return type_.to_dict(details, inflated)
        else:
          types = self.attribute_definition_controller.get_all_types()
          result = list()
          for type_ in types:
            result.append(type_.to_dict(details, inflated))
          return result
      elif method == 'POST':
        if len(path) > 0:
          raise RestHandlerException(u'No post definied on the given path')
        else:
          # Add new type
          type_ = AttributeType()
          type_.populate(json)
          # set the new checksum
          self.attribute_definition_controller.insert_type(type_)
          return type_.to_dict(details, inflated)
      elif method == 'PUT':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          type_ = self.attribute_definition_controller.get_type_by_id(uuid)
          type_.populate(json)
          self.attribute_definition_controller.update_type(type_)
          return type_.to_dict(details, inflated)
        else:
          raise RestHandlerException(u'Cannot update type as no identifier was given')
      elif method == 'DELETE':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          self.attribute_definition_controller.remove_type_by_id(uuid)
          return 'OK'
        else:
          raise RestHandlerException(u'Cannot delete type as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
