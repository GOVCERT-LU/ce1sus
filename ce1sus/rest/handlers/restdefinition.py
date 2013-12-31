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
from ce1sus.brokers.definition.handlerdefinitionbroker import \
                                                      AttributeHandlerBroker

class RestDefinitionController(RestControllerBase):

  PARAMETER_INSERT_MAPPER = {'attribute': 'updateAttributeDefinitions',
                             'object': 'updateObejctDefinitions'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.attributeDefinitionBroker = self.brokerFactory(
                                                    AttributeDefinitionBroker
                                                       )
    self.objectDefinitionBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.handlerBroker = self.brokerFactory(AttributeHandlerBroker)

  def getFunctionName(self, parameter, action):
    if action == 'POST':
      return RestDefinitionController.PARAMETER_INSERT_MAPPER.get(parameter,
                                                                   None)
    return None

  def updateAttributeDefinitions(self, identifier, apiKey, **options):
    self._checkIfPriviledged(apiKey)
    fullDefinition = options.get('fulldefinitions', False)
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
    fullDefinition = options.get('fulldefinitions', False)
    restDefinition = self.getPostObject()
    try:
      definition = self.objectDefinitionBroker.buildObjectDefinition(
                               identifier=None,
                               name=restDefinition.name,
                               description=restDefinition.description,
                               action='insert',
                               share=1,
                               )
      # check if existing
      try:
        # continue
        definition = self.objectDefinitionBroker.getDefintionByCHKSUM(definition.chksum)
      except NothingFoundException:
        # insert
        self.objectDefinitionBroker.insert(definition, False)

      # insert attributes if there are:
      for restAttribtue in restDefinition.attributes:
        attribute = self.attributeDefinitionBroker.buildAttributeDefinition(identifier=None,
                               name=restAttribtue.name,
                               description=restAttribtue.description,
                               regex=restAttribtue.regex,
                               classIndex=restAttribtue.classIndex,
                               action='insert',
                               handlerIndex=restAttribtue.handlerIndex,
                               share=1,
                               relation=restAttribtue.relation)
        # check if attribute exists
        try:
          # continue
          attribute = self.attributeDefinitionBroker.getDefintionByCHKSUM(attribute.chksum)
        except NothingFoundException:
          # insert
          # check if handler and class index exist
          if not attribute.isClassIndexExisting(attribute.classIndex):
            self.raiseError('UnknownDefinitionException', 'Cannot Insert Attribute as ClassIndex {0} does not exist'.format(attribute.classIndex))
          if not self.handlerBroker.ishandlerIndexExisting(attribute.handlerIndex):
            self.raiseError('UnknownDefinitionException', 'Cannot Insert Attribute as HanlderIndex {0} does not exist'.format(attribute.handlerIndex))
          self.attributeDefinitionBroker.insert(attribute, False)

        definition.attributes.append(attribute)

      self.objectDefinitionBroker.doCommit(True)
      obj = self._objectToJSON(definition,
                               True,
                               fullDefinition,
                               False)
      return self._returnMessage(obj)
    except BrokerException as e:
        return self.raiseError('BrokerException', e)
