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

  PARAMETER_MAPPER = {'attributes': 'viewAttributesDefinitions',
                      'objects': 'viewObejctsDefinitions'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.attributeDefinitionBroker = self.brokerFactory(
                                                      AttributeDefinitionBroker
                                                       )
    self.objectDefinitionBroker = self.brokerFactory(ObjectDefinitionBroker)

  def getFunctionName(self, parameter, action):
    if action == 'GET':
      return RestDefinitionsController.PARAMETER_MAPPER.get(parameter, None)
    return None

  def __getDefinition(self, broker, chksums, fullDefinition):
    try:
      if chkSums:
        definitions = broker.getDefintionByCHKSUMS(chkSums)
      else:
        definitions = broker.getAll()

      result = list()
      for definition in definitions:
        obj = self._objectToJSON(definition,
                               True,
                               fullDefinition,
                               True)
        result.append(obj)
      if result:
        return self._returnList(result)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def viewAttributesDefinitions(self, identifier, apiKey, **options):
    self.checkIfPriviledged(self.getUserByAPIKey(apiKey))
    fullDefinition = options.get('fulldefinitions', False)
    chkSums = options.get('chksum', list())
    return self.__getDefinition(self.attributeDefinitionBroker,
                                chkSums,
                                fullDefinition)

  def viewObejctsDefinitions(self, identifier, apiKey, **options):
    self.checkIfPriviledged(self.getUserByAPIKey(apiKey))
    fullDefinition = options.get('fulldefinitions', False)
    chkSums = options.get('chksum', list())
    return self.__getDefinition(self.objectDefinitionBroker,
                                chkSums,
                                fullDefinition)