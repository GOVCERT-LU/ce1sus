# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 24, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.rest.handlers.restbase import RestBaseHandler
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.controllers.event.attributes import AttributesController
from ce1sus.controllers.event.objects import ObjectsController
from dagr.controllers.base import ControllerException


class RestDefinitionHanldler(RestBaseHandler):

  PARAMETER_INSERT_MAPPER = {'attribute': 'insert_attribute_definitions',
                             'object': 'insert_object_definitions'}

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attributes_controller = AttributesController(config)
    self.objects_controller = ObjectsController(config)

  # pylint: disable=R0201
  def get_function_name(self, parameter, action):
    if action == 'POST':
      return RestDefinitionHanldler.PARAMETER_INSERT_MAPPER.get(parameter,
                                                                   None)
    return None

  def insert_attribute_definitions(self, identifier, **options):
    self._check_if_priviledged()
    full_definition = options.get('fulldefinitions', False)
    try:
      rest_attribute_definition = self.get_post_object()
      user = self._get_user()
      attribute_definition = self.convert_to_db_Object(rest_attribute_definition, user, 'insert')
      attribute_definition, valid = self.attributes_controller.insert_definition(user, attribute_definition)
      if not valid:
        self._raise_invalid_error(attribute_definition)
      return self.return_object(attribute_definition, True, full_definition, True)
    except ControllerException as error:
      return self._raise_error('ControllerException', error=error)

  def insert_object_definitions(self, identifier, **options):
    self._check_if_priviledged()
    full_definition = options.get('fulldefinitions', False)
    try:
      rest_object_definition = self.get_post_object()
      user = self._get_user()
      object_definition = self.convert_to_db_Object(rest_object_definition, user, 'insert')
      object_definition, valid = self.objects_controller.insert_definition(user, object_definition)
      if not valid:
        self._raise_invalid_error(object_definition)
      return self.return_object(object_definition, True, full_definition, True)
    except ControllerException as error:
      return self._raise_error('ControllerException', error=error)
