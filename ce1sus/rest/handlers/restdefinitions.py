# -*- coding: utf-8 -*-

"""
(Description)

Created on Dec 24, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


import cherrypy
from ce1sus.rest.restbase import RestControllerBase
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.definition.attributedefinitionbroker import AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import ObjectDefinitionBroker


class RestDefinitionsController(RestControllerBase):

  PARAMETER_MAPPER = {'attribute':'viewAttributeDefinitions',
                      'object':'viewObejctDefinitions'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.attributeDefinitionBroker = self.brokerFactory(AttributeDefinitionBroker)
    self.objectDefinitionBroker = self.brokerFactory(ObjectDefinitionBroker)

  def getFunctionName(self, parameter, action):
    if action == 'GET':
      return RestDefinitionsController.PARAMETER_MAPPER.get(parameter, None)
    return None

  def viewAttributeDefinitions(self, identifier, apiKey, **options):
    try:
      self._checkIfPriviledged(apiKey)
      fullDefinition = options.get('Full-Definitions', False)
      chkSums = options.get('chksum', list())
      if chkSums:
        attributes = self.attributeDefinitionBroker.getDefintionByCHKSUMS(identifier)
      else:
        attributes = self.attributeDefinitionBroker.getAll()

      obj = self._objectToJSON(attributes,
                                 True,
                                 fullDefinition,
                                 True)
      return self._returnMessage(obj)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def viewObejctDefinitions(self, identifier, apiKey, **options):
    try:
      self._checkIfPriviledged(apiKey)
      fullDefinition = options.get('Full-Definitions', False)
      chkSums = options.get('chksum', list())
      if chkSums:
        defObjects = self.objectDefinitionBroker.getDefintionByCHKSUMS(identifier)
      else:
        defObjects = self.objectDefinitionBroker.getAll()

      obj = self._objectToJSON(defObjects,
                               True,
                               fullDefinition,
                               True)
      return self._returnMessage(obj)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)
