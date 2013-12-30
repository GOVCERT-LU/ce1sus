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

  def viewAttributesDefinitions(self, identifier, apiKey, **options):
    try:
      self._checkIfPriviledged(apiKey)
      fullDefinition = options.get('Full-Definitions', False)
      chkSums = options.get('chksum', list())
      if chkSums:
        defAttributes = self.attributeDefinitionBroker.getDefintionByCHKSUMS(
                                                                        chkSums
                                                                         )
      else:
        defAttributes = self.attributeDefinitionBroker.getAll()

      result = list()
      for defAttribute in defAttributes:
        obj = self._objectToJSON(defAttribute,
                               True,
                               fullDefinition,
                               True)
        result.append(obj)

      return self._returnList(result)

    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def viewObejctsDefinitions(self, identifier, apiKey, **options):
    try:
      self._checkIfPriviledged(apiKey)
      fullDefinition = options.get('Full-Definitions', False)
      chkSums = options.get('chksum', list())
      if chkSums:
        defObjects = self.objectDefinitionBroker.getDefintionByCHKSUMS(chkSums)
      else:
        defObjects = self.objectDefinitionBroker.getAll()

      result = list()
      for defObject in defObjects:
        obj = self._objectToJSON(defObject,
                               True,
                               fullDefinition,
                               True)
        result.append(obj)

      return self._returnList(result)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)
