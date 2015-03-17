# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
from ce1sus.common.system import APP_REL, DB_REL, REST_REL
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.controllers.events.attributecontroller import AttributeController
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, valid_uuid
from ce1sus.views.web.common.decorators import privileged


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class VersionHandler(RestBaseHandler):

  @rest_method(default=True)
  @methods(allowed=['GET'])
  def version(self, **args):

    result = dict()
    result['application'] = APP_REL
    result['dataBase'] = DB_REL
    result['restApi'] = REST_REL
    return result


class HandlerHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attribute_definition_controller = AttributeDefinitionController(config)
    self.attribute_controller = AttributeController(config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def handlers(self, **args):
    path = args.get('path')
    parameters = args.get('parameters')
    if len(path) == 0:
      self.check_if_admin()
      handlers = self.attribute_definition_controller.get_all_handlers()
      result = list()
      for handler in handlers:
        result.append(handler.to_dict())
      return result
    else:
      if len(path) > 1:
        definition_uuid = path.pop(0)
        if valid_uuid(definition_uuid):
          definition = self.attribute_definition_controller.get_attribute_definitions_by_uuid(definition_uuid)
          handler = definition.handler
          handler.user = self.get_user()
          method = path.pop(0)
          # has nothing to do with the http method which is in capital
          if method == 'get':
            if len(path) > 0:
              attr_uuid = path.pop(0)
              if valid_uuid(attr_uuid):
                attribute = self.attribute_controller.get_attribute_by_uuid(attr_uuid)
              else:
                raise RestHandlerException(u'Specified second uuid is invalid')
            else:
              attribute = None
            # Make the generic call for additional data
            return handler.get_data(attribute, definition, parameters)
          else:
            raise RestHandlerException(u'Method {0} is not specified'.format(method))
        else:
          raise RestHandlerException(u'Specified uuid is invalid')
      else:
        raise RestHandlerException(u'Invalid request')


class ReferenceHandlerHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.reference_controller = ReferencesController(config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def handlers(self, **args):
    path = args.get('path')
    parameters = args.get('parameters')
    if len(path) == 0:
      self.check_if_admin()
      handlers = self.reference_controller.get_all_handlers()
      result = list()
      for handler in handlers:
        result.append(handler.to_dict())
      return result
    else:
      if len(path) > 1:
        definition_uuid = path.pop(0)
        if valid_uuid(definition_uuid):
          definition = self.reference_controller.get_reference_definitions_by_uuid(definition_uuid)
          handler = definition.handler
          handler.user = self.get_user()
          method = path.pop(0)
          # has nothing to do with the http method which is in capital
          if method == 'get':
            if len(path) > 0:
              attr_uuid = path.pop(0)
              if valid_uuid(attr_uuid):
                reference = self.reference_controller.get_reference_by_uuid(attr_uuid)
              else:
                raise RestHandlerException(u'Specified second uuid is invalid')
            else:
              reference = None
            # Make the generic call for additional data
            return handler.get_data(reference, definition, parameters)
          else:
            raise RestHandlerException(u'Method {0} is not specified'.format(method))
        else:
          raise RestHandlerException(u'Specified uuid is invalid')
      else:
        raise RestHandlerException(u'Invalid request')


class TablesHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attribute_definition_controller = AttributeDefinitionController(config)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def tables(self, **args):
    values = self.attribute_definition_controller.get_all_tables()
    result = list()
    for key, value in values.iteritems():
      result.append({'identifier': key, 'name': value})
    return result
