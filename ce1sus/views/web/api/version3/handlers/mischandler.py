# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2014
"""
from ce1sus.common.system import APP_REL, DB_REL, REST_REL
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require
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

  @rest_method(default=True)
  @methods(allowed=['GET'])
  @require(privileged())
  def handlers(self, **args):
    handlers = self.attribute_definition_controller.get_all_handlers()
    result = list()
    for handler in handlers:
      result.append(handler.to_dict())
    return result


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
