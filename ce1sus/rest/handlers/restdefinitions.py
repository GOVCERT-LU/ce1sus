# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 24, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.rest.restbase import RestControllerBase
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                    AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                                                    ObjectDefinitionBroker


class RestDefinitionsController(RestControllerBase):

  PARAMETER_MAPPER = {'attributes': 'view_attributes_definitions',
                      'objects': 'view_obejcts_definitions'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.attribute_definition_broker = self.broker_factory(
                                                      AttributeDefinitionBroker
                                                       )
    self.object_definition_broker = self.broker_factory(ObjectDefinitionBroker)

  def get_function_name(self, parameter, action):
    if action == 'GET':
      return RestDefinitionsController.PARAMETER_MAPPER.get(parameter, None)
    return None

  def __get_definition(self, broker, chksums, full_definition):
    try:
      if chksums:
        definitions = broker.get_defintion_by_chksums(chksums)
      else:
        definitions = broker.get_all()

      result = list()
      for definition in definitions:
        obj = self._object_to_json(definition,
                               True,
                               full_definition,
                               True)
        result.append(obj)
      if result:
        return self._return_list(result)
    except NothingFoundException as error:
      return self.raise_error('NothingFoundException', error)
    except BrokerException as error:
      return self.raise_error('BrokerException', error)

  def view_attributes_definitions(self, identifier, api_key, **options):
    self.checkIfPriviledged(self.getUserByAPIKey(api_key))
    full_definition = options.get('fulldefinitions', False)
    chksums = options.get('chksum', list())
    return self.__get_definition(self.attribute_definition_broker,
                                chksums,
                                full_definition)

  def view_obejcts_definitions(self, identifier, api_key, **options):
    self.checkIfPriviledged(self.getUserByAPIKey(api_key))
    full_definition = options.get('fulldefinitions', False)
    chksums = options.get('chksum', list())
    return self.__get_definition(self.object_definition_broker,
                                chksums,
                                full_definition)
