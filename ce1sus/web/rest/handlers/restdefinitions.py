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


class RestDefinitionsHanldler(RestBaseHandler):

  PARAMETER_MAPPER = {'attributes': 'view_attributes_definitions',
                      'objects': 'view_obejcts_definitions'}

  def __init__(self, config):
    RestBaseHandler.__init__(self, config)
    self.attributes_controller = AttributesController(config)
    self.objects_controller = ObjectsController(config)

  def get_function_name(self, parameter, action):
    if action == 'GET':
      return RestDefinitionsHanldler.PARAMETER_MAPPER.get(parameter, None)
    return None

  def __get_definition(self, controller, chksums, full_definition):
    try:
      if chksums:
        definitions = controller.get_defintion_by_chksums(chksums)
      else:
        definitions = controller.get_all()

      result = list()
      user = self._get_user()
      if isinstance(definitions, list):
        for definition in definitions:
          result.append(self.create_rest_obj(definition, user, full_definition, True))
      else:
        result.append(self.create_rest_obj(definitions, user, full_definition, True))
      result_dict = {'Results': result}
      return self.create_return_msg(result_dict)
    except ControllerException as error:
      return self._raise_error('ControllerException', error)

  def view_attributes_definitions(self, identifier, **options):
    self._check_if_priviledged()
    full_definition = options.get('fulldefinitions', False)
    chksums = options.get('chksum', list())
    return self.__get_definition(self.attributes_controller,
                                chksums,
                                full_definition)

  def view_obejcts_definitions(self, identifier, **options):
    self._check_if_priviledged()
    full_definition = options.get('fulldefinitions', False)
    chksums = options.get('chksum', list())
    return self.__get_definition(self.objects_controller,
                                chksums,
                                full_definition)
