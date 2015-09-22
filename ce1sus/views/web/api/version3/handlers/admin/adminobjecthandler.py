# -*- coding: utf-8 -*-

"""
(Description)

Created on Nov 3, 2014
"""
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.internal.definitions import ObjectDefinition, ChildObjectDefintion
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminObjectHandler(RestBaseHandler):

  def __init__(self, config):
    super(AdminObjectHandler, self).__init__(config)
    self.object_definition_controller = self.controller_factory(ObjectDefinitionController)
    self.attribute_definition_controller = self.controller_factory(AttributeDefinitionController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def object(self, **args):
    try:
      method = args.get('method')
      path = args.get('path')
      json = args.get('json')
      cache_object = self.get_cache_object(args)
      if method == 'GET':
        if len(path) > 0:
                    # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          # TODO: add inflate
          definition = self.object_definition_controller.get_object_definitions_by_uuid(uuid)
          if len(path) > 0:
            type_ = uuid = path.pop(0)
            if type_ == 'attribute':
              if len(path) > 0:
                raise RestHandlerException(u'Use the attribute api instead')
              else:
                result = list()
                for attribute in definition.attributes:
                  result.append(attribute.to_dict(cache_object))
                return result
            else:
              raise RestHandlerException(u'"{0}" is not supported'.format(type_))
          else:
            return definition.to_dict(cache_object)
        else:
          # else return all
          definitions = self.object_definition_controller.get_all_object_definitions()
          result = list()
          for definition in definitions:
            result.append(definition.to_dict(cache_object))
          return result
      elif method == 'POST':
        self.check_if_admin()
        if len(path) > 0:
          uuid = path.pop(0)
          definition = self.object_definition_controller.get_object_definitions_by_uuid(uuid)
          if len(path) > 0:
            type_ = path.pop(0)
            if type_ == 'attribute':
              # get the object definition
              if isinstance(json, list):
                # TODO: add support for lists
                raise RestHandlerException(u'POST of object attributes does not support lists')

              uuid = json.get('identifier', None)
              if uuid:
                attr = self.attribute_definition_controller.get_attribute_definitions_by_uuid(uuid)
                definition.attributes.append(attr)
                self.object_definition_controller.update_object_definition(definition, self.get_user())
                return 'OK'
              else:
                raise RestHandlerException(u'No id was specified in the json post')
            elif type_ == 'object':
              if isinstance(json, list):
                # TODO: add support for lists
                raise RestHandlerException(u'POST of object objects does not support lists')

              child_def = json.get('definition', None)
              if child_def:
                uuid = child_def.get('identifier', None)
                if uuid:
                  if uuid == definition.uuid:
                    raise RestHandlerException('Cannot add definition to child')
                  child_object = self.assembler.assemble(json, ChildObjectDefintion, definition, cache_object)
                  definition.objects.append(child_object)
                  self.object_definition_controller.update_object_definition(definition)
                  return 'OK'
                else:
                  raise RestHandlerException(u'No id was specified in the definition of the json post')
              else:
                raise RestHandlerException(u'No definition was specified in the json post')
            else:
              raise RestHandlerException(u'"{0}" is not supported'.format(type_))
          else:
            raise RestHandlerException(u'If an id was specified you also must specify on which type it is associated')
        else:
          # Add new user
          obj_def = self.assembler.assemble(json, ObjectDefinition, None, cache_object)
          # set the new checksum
          self.object_definition_controller.insert_object_definition(obj_def, self.get_user())
          return obj_def.to_dict(cache_object)
      elif method == 'PUT':
        self.check_if_admin()
        # update user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          obj_def = self.object_definition_controller.get_object_definitions_by_uuid(uuid)
          if len(path) > 0:
            type_ = path.pop(0)
            if len(path) > 0:
              uuid = path.pop(0)
              child = self.object_definition_controller.get_child_object_definitions_by_uuid(uuid)
              self.updater.update(child, json, cache_object)
              self.object_definition_controller.update_child_object_definition(obj_def, child)
            else:
              raise RestHandlerException(u'No uuid given')
          else:
            self.updater.update(obj_def, json, cache_object)
            # set the new checksum
            self.object_definition_controller.update_object_definition(obj_def)
          return obj_def.to_dict(cache_object)
        else:
          raise RestHandlerException(u'Cannot update user as no identifier was given')

      elif method == 'DELETE':
        self.check_if_admin()
        # Remove user
        if len(path) > 0:
          # if there is a uuid as next parameter then return single user
          uuid = path.pop(0)
          if len(path) > 0:
            type_ = path.pop(0)
            if type_ == 'attribute':
              definition = self.object_definition_controller.get_object_definitions_by_uuid(uuid)
              uuid = path.pop(0)
              attr = self.attribute_definition_controller.get_attribute_definitions_by_uuid(uuid)
              definition.attributes.remove(attr)
              self.object_definition_controller.update_object_definition(definition)
            elif type_ == 'object':
              definition = self.object_definition_controller.get_object_definitions_by_uuid(uuid)
              uuid = path.pop(0)
              self.object_definition_controller.remove_child_object_definitions_by_uuid(uuid)

            else:
              raise RestHandlerException(u'If an id was specified you also must specify on which type it is associated')
          else:
            self.object_definition_controller.remove_definition_by_uuid(uuid)

          return 'OK'
        else:
          raise RestHandlerException(u'Cannot delete user as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
