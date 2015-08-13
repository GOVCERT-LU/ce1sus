# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 30, 2014
"""
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.db.classes.internal.report import ReferenceDefinition
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminReferenceDefinitionHandler(RestBaseHandler):

  def __init__(self, config):
    super(AdminReferenceDefinitionHandler, self).__init__(config)
    self.reference_controller = self.controller_factory(ReferencesController)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require()
  def reference(self, **args):
    try:
      method = args.get('method')
      json = args.get('json')
      path = args.get('path')
      cache_object = self.get_cache_object(args)
      if method == 'GET':
        if len(path) > 0:
                    # if there is a uuid as next parameter then return single mail
          uuid = path.pop(0)
          reference = self.reference_controller.get_reference_definitions_by_uuid(uuid)
          return reference.to_dict(cache_object)
        else:
          # return all
          references = self.reference_controller.get_reference_definitions_all()
          result = list()
          for reference in references:
            result.append(reference.to_dict(cache_object))
          return result
      elif method == 'PUT':
        self.check_if_admin()
        if len(path) > 0:
          uuid = path.pop(0)
          reference = self.reference_controller.get_reference_definitions_by_uuid(uuid)
          self.updater.update(reference, json, cache_object)
          self.reference_controller.update_reference_definition(reference)
          return reference.to_dict(cache_object)
        else:
          raise RestHandlerException(u'Cannot update reference as no identifier was given')
      elif method == 'POST':
        self.check_if_admin()
        if len(path) > 0:
          raise RestHandlerException(u'Cannot insert reference as an identifier was given')
        else:
          reference = self.assembler.assemble(json, ReferenceDefinition, None, cache_object)
          self.reference_controller.insert_reference_definition(reference, self.get_user())
          return reference.to_dict(cache_object)

      elif method == 'DELETE':
        self.check_if_admin()
        if len(path) > 0:
          uuid = path.pop(0)
          self.reference_controller.remove_reference_definition_by_uuid(uuid)
          return 'OK'
        else:
          raise RestHandlerException(u'Cannot remove reference as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
