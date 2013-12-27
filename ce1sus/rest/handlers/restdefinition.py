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


class RestDefinitionController(RestControllerBase):

  PARAMETER_MAPPER = {'attribute': 'viewAttributeDefinition',
                      'object': 'viewObejctDefinition'}
  PARAMETER_INSERT_MAPPER = {'attribute': 'updateAttributeDefinitions',
                             'object': 'updateObejctDefinitions'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.attributeDefinitionBroker = self.brokerFactory(
                                                    AttributeDefinitionBroker
                                                       )
    self.objectDefinitionBroker = self.brokerFactory(ObjectDefinitionBroker)

  def getFunctionName(self, parameter, action):
    if action == 'GET':
      return RestDefinitionController.PARAMETER_MAPPER.get(parameter, None)
    if action == 'PUT':
      return RestDefinitionController.PARAMETER_INSERT_MAPPER.get(parameter,
                                                                   None)
    return None

  def viewAttributeDefinition(self, identifier, apiKey, **options):
    try:
      self._checkIfPriviledged(apiKey)
      fullDefinition = options.get('Full-Definitions', False)
      attribute = self.attributeDefinitionBroker.getDefintionByCHKSUM(
                                                                    identifier
                                                                     )
      obj = self._objectToJSON(attribute,
                               True,
                               fullDefinition,
                               True)
      return self._returnMessage(obj)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def viewObejctDefinition(self, identifier, apiKey, **options):
    try:
      self._checkIfPriviledged(apiKey)
      fullDefinition = options.get('Full-Definitions', False)
      defObject = self.objectDefinitionBroker.getDefintionByCHKSUM(identifier)
      obj = self._objectToJSON(defObject,
                               True,
                               fullDefinition,
                               True)
      return self._returnMessage(obj)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def updateAttributeDefinitions(self, identifier, apiKey, **options):
    self._checkIfPriviledged(apiKey)
    fullDefinition = options.get('Full-Definitions', False)
    restDefinition = self.getPostObject()
    try:
      definition = self.attributeDefinitionBroker.buildAttributeDefinition(
                               identifier=None,
                               name=restDefinition.name,
                               description=restDefinition.description,
                               regex=restDefinition.regex,
                               classIndex=restDefinition.classIndex,
                               action='insert',
                               handlerIndex=restDefinition.handlerIndex,
                               share=1,
                               relation=1)
      self.attributeDefinitionBroker.insert(definition, True)
      obj = self._objectToJSON(definition,
                               True,
                               fullDefinition,
                               False)
      return self._returnMessage(obj)
    except BrokerException as e:
        return self.raiseError('BrokerException', e)

  def updateObejctDefinitions(self, identifier, apiKey, **options):
    self._checkIfPriviledged(apiKey)
    fullDefinition = options.get('Full-Definitions', False)
    restDefinition = self.getPostObject()
    try:
      definition = self.objectDefinitionBroker.buildObjectDefinition(
                               identifier=None,
                               name=restDefinition.name,
                               description=restDefinition.description,
                               action='insert',
                               share=1,
                               )
      self.objectDefinitionBroker.insert(definition, True)
      obj = self._objectToJSON(definition,
                               True,
                               fullDefinition,
                               False)
      return self._returnMessage(obj)
    except BrokerException as e:
        return self.raiseError('BrokerException', e)
