# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 3, 2014
"""
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.definitions import ObjectDefinition
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminObjectHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.object_definition_controller = ObjectDefinitionController(config)
    self.attribute_definition_controller = AttributeDefinitionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require(privileged())
  def object(self, **args):
    try:
      method = args.get('method')
      path = args.get('path')
      headers = args.get('headers')
      details = headers.get('Complete', 'false')
      json = args.get('json')
      if details == 'true':
        details = True
      else:
        details = False
      if method == 'GET':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          # TODO: add inflate
          definition = self.object_definition_controller.get_object_definitions_by_id(uuid)
          if len(path) > 0:
            type_ = uuid = path.pop(0)
            if type_ == 'attribute':
              if len(path) > 0:
                raise RestHandlerException(u'Use the object api instead')
              else:
                result = list()
                for attribute in definition.attribute:
                  result.append(attribute.to_dict(complete=details))
                return result
            else:
              raise RestHandlerException(u'"{0}" is not supported'.format(type))
          else:
            return definition.to_dict(complete=details)
        else:
          # else return all
          definitions = self.object_definition_controller.get_all_object_definitions()
          result = list()
          for definition in definitions:
            if details == 'true':
              result.append(definition.to_dict())
            else:
              result.append(definition.to_dict(complete=False))
          return result
      elif method == 'POST':
        if len(path) > 0:
          uuid = path.pop(0)
          definition = self.object_definition_controller.get_object_definitions_by_id(uuid)
          if len(path) > 0:
            type_ = path.pop(0)
            # get the object definition
            if isinstance(json, list):
              # TODO: add support for lists
              raise RestHandlerException(u'POST of object attributes does not support lists')

            uuid = json.get('identifier', None)
            if uuid:
              attr = self.attribute_definition_controller.get_attribute_definitions_by_id(uuid)
              definition.attributes.append(attr)
              self.object_definition_controller.update_object_definition(definition, self.get_user())
              return 'OK'
            else:
              raise RestHandlerException(u'No id was specified in the json post')
          else:
            raise RestHandlerException(u'If an id was specified you also must specify on which type it is associated')
        else:
          # Add new user
          obj_def = ObjectDefinition()
          obj_def.populate(json)
          # set the new checksum
          self.object_definition_controller.insert_object_definition(obj_def, self.get_user())
          return obj_def.to_dict()
      elif method == 'PUT':
        # update user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          obj_def = self.object_definition_controller.get_object_definitions_by_id(uuid)
          obj_def.populate(json)
          # set the new checksum
          self.object_definition_controller.update_object_definition(obj_def, self.get_user())
          return obj_def.to_dict()
        else:
          raise RestHandlerException(u'Cannot update user as no identifier was given')

      elif method == 'DELETE':
        # Remove user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          if len(path) > 0:
            type_ = path.pop(0)
            if len(path) > 0:
              definition = self.object_definition_controller.get_object_definitions_by_id(uuid)
              uuid = path.pop(0)
              attr = self.attribute_definition_controller.get_attribute_definitions_by_id(uuid)
              definition.attributes.remove(attr)
              self.object_definition_controller.update_object_definition(definition, self.get_user())
            else:
              raise RestHandlerException(u'If an id was specified you also must specify on which type it is associated')
          else:
            self.object_definition_controller.remove_definition_by_id(uuid)

          return 'OK'
        else:
          raise RestHandlerException(u'Cannot delete user as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
