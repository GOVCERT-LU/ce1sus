# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 30, 2014
"""
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.controllers.base import ControllerException, ControllerNothingFoundException
from ce1sus.views.web.api.version3.handlers.restbase import RestBaseHandler, rest_method, methods, require, RestHandlerException, RestHandlerNotFoundException
from ce1sus.views.web.common.decorators import privileged
from ce1sus.db.classes.report import ReferenceDefinition


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class AdminReferenceDefinitionHandler(RestBaseHandler):

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.reference_controller = ReferencesController(config)

  @rest_method(default=True)
  @methods(allowed=['GET', 'PUT', 'POST', 'DELETE'])
  @require(privileged())
  def reference(self, **args):
    try:
      method = args.get('method')
      json = args.get('json')
      path = args.get('path')
      details = self.get_detail_value(args)
      inflated = self.get_inflated_value(args)
      if method == 'GET':
        if len(path) > 0:
          # if there is a uuid as next parameter then return single mail
          uuid = path.pop(0)
          reference = self.reference_controller.get_reference_definitions_by_uuid(uuid)
          return reference.to_dict(details, inflated)
        else:
          # return all
          references = self.reference_controller.get_all()
          result = list()
          for reference in references:
            result.append(reference.to_dict(details, inflated))
          return result
      elif method == 'PUT':
        self.check_if_admin()
        if len(path) > 0:
          uuid = path.pop(0)
          reference = self.reference_controller.get_reference_definitions_by_uuid(uuid)
          reference.populate(json)
          self.reference_controller.update_reference_definition(reference, self.get_user())
          return reference.to_dict(details, inflated)
        else:
          raise RestHandlerException(u'Cannot update reference as no identifier was given')
      elif method == 'POST':
        self.check_if_admin()
        if len(path) > 0:
          raise RestHandlerException(u'Cannot insert reference as an identifier was given')
        else:
          reference = ReferenceDefinition()
          reference.populate(json)
          self.reference_controller.insert_reference_definition(reference, self.get_user())
          return reference.to_dict(details, inflated)

      elif method == 'DELETE':
        self.check_if_admin()
        if len(path) > 0:
          uuid = path.pop(0)
          self.reference_controller.remove_reference_definition_by_uuid(uuid)
        else:
          raise RestHandlerException(u'Cannot remove reference as no identifier was given')
      raise RestHandlerException(u'Unrecoverable error')
    except ControllerNothingFoundException as error:
      raise RestHandlerNotFoundException(error)
    except ControllerException as error:
      raise RestHandlerException(error)
