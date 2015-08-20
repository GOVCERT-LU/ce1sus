# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
from ce1sus.common.system import APP_REL, DB_REL, REST_REL
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.controllers.admin.syncserver import SyncServerController
from ce1sus.controllers.events.attributecontroller import AttributeController
from ce1sus.db.classes.internal.common import TLP
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, valid_uuid
from ce1sus.views.web.common.decorators import privileged
from ce1sus.controllers.admin.group import GroupController


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
    result['environment'] = self.config.get('ce1sus', 'environment', 'LOCAL_DEV')
    return result


class HandlerHandler(RestBaseHandler):

  def __init__(self, config):
    super(HandlerHandler, self).__init__(config)
    self.attribute_definition_controller = self.controller_factory(AttributeDefinitionController)
    self.attribute_controller = self.controller_factory(AttributeController)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def handlers(self, **args):
    path = args.get('path')
    parameters = args.get('parameters')
    cache_object = self.get_cache_object(args)
    if len(path) == 0:
      self.check_if_admin()
      handlers = self.attribute_definition_controller.get_all_handlers()
      result = list()
      for handler in handlers:
        result.append(handler.to_dict(cache_object))
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
    super(ReferenceHandlerHandler, self).__init__(config)
    self.reference_controller = self.controller_factory(ReferencesController)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require()
  def handlers(self, **args):
    path = args.get('path')
    parameters = args.get('parameters')
    cache_object = self.get_cache_object(args)
    if len(path) == 0:
      self.check_if_admin()
      handlers = self.reference_controller.get_all_handlers()
      result = list()
      for handler in handlers:
        result.append(handler.to_dict(cache_object))
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
    super(TablesHandler, self).__init__(config)
    self.attribute_definition_controller = self.controller_factory(AttributeDefinitionController)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def tables(self, **args):
    values = self.attribute_definition_controller.get_all_tables()
    result = list()
    for key, value in values.iteritems():
      result.append({'identifier': key, 'name': value})
    return result


class TLPHandler(RestBaseHandler):

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def tlps(self, **args):
    values = TLP.get_dictionary()
    result = list()
    for key, value in values.iteritems():
      result.append({'identifier': key, 'name': value})
    return result


class SyncServerTypesHandler(RestBaseHandler):

  def __init__(self, config):
    super(SyncServerTypesHandler, self).__init__(config)
    self.sync_server_controller = self.controller_factory(SyncServerController)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def types(self, **args):
    values = self.sync_server_controller.get_all_types()
    result = list()
    for key, value in values.iteritems():
      result.append({'identifier': key, 'name': value})
    return result

class UserGroupsHandler(RestBaseHandler):

  def __init__(self, config):
    super(UserGroupsHandler, self).__init__(config)
    self.group_controller = self.controller_factory(GroupController)

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def usergroups(self, **args):
    groups = self.group_controller.get_all_groups()
    result = list()
    cache_object = self.get_cache_object(args)
    if groups:
      result = groups[0].attributelist_to_dict(groups, cache_object)
    return result
