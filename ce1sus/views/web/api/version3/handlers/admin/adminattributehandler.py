# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 3, 2014
"""
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.definitions import AttributeDefinition
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminAttributeHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attribute_definition_controller = AttributeDefinitionController(config)
    self.object_definition_controller = ObjectDefinitionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require(privileged())
  def attribute(self, **args):
    try:
      method = args.get('method')
      path = args.get('path')
      json = args.get('json')
      details = self.get_detail_value(args)
      if method == 'GET':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          # TODO: add inflate
          definition = self.attribute_definition_controller.get_attribute_definitions_by_id(uuid)
          if len(path) > 0:
            type_ = uuid = path.pop(0)
            if type_ == 'object':
              if len(path) > 0:
                raise RestHandlerException(u'Use the object api instead')
              else:
                result = list()
                for obj in definition.objects:
                  result.append(obj.to_dict(complete=details))
                return result
            else:
              raise RestHandlerException(u'"{0}" is not supported'.format(type_))
          else:
            return definition.to_dict(complete=details)
        else:
          # else return all

          definitions = self.attribute_definition_controller.get_all_attribute_definitions()
          result = list()
          for definition in definitions:
            result.append(definition.to_dict(details))
          return result
      elif method == 'POST':
        if len(path) > 0:
          uuid = path.pop(0)
          definition = self.attribute_definition_controller.get_attribute_definitions_by_id(uuid)
          if len(path) > 0:
            type_ = path.pop(0)
            if type_ == 'object':
              # get the object definition
              if isinstance(json, list):
                # TODO: add support for lists
                raise RestHandlerException(u'POST of attribute objects does not support lists')
              uuid = json.get('identifier', None)
              if uuid:
                obj = self.object_definition_controller.get_object_definitions_by_id(uuid)
                definition.objects.append(obj)
                self.attribute_definition_controller.update_attribtue_definition(definition, self.get_user())
                return 'OK'
              else:
                raise RestHandlerException(u'No id was specified in the json post')
            else:
              raise RestHandlerException(u'"{0}" is not supported'.format(type_))
          else:
            raise RestHandlerException(u'If an id was specified you also must specify on which type it is associated')
        else:
          # Add new user
          attr_def = AttributeDefinition()
          attr_def.populate(json)
          # set the new checksum
          self.attribute_definition_controller.insert_attribute_definition(attr_def, self.get_user())
          return attr_def.to_dict()
      elif method == 'PUT':
        # update user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          attr_def = self.attribute_definition_controller.get_attribute_definitions_by_id(uuid)
          attr_def.populate(json)
          # set the new checksum
          self.attribute_definition_controller.update_attribtue_definition(attr_def, self.get_user())
          return attr_def.to_dict()
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
              definition = self.attribute_definition_controller.get_attribute_definitions_by_id(uuid)
              uuid = path.pop(0)
              obj = self.object_definition_controller.get_object_definitions_by_id(uuid)
              definition.objects.remove(obj)
              self.attribute_definition_controller.update_attribtue_definition(definition, self.get_user())

            else:
              raise RestHandlerException(u'If an id was specified you also must specify on which type it is associated')
          else:
            self.attribute_definition_controller.remove_definition_by_id(uuid)

          return 'OK'
        else:
          raise RestHandlerException(u'Cannot delete user as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
