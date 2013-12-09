# -*- coding: utf-8 -*-

"""

Created on Oct 8, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from ce1sus.rest.restbase import RestControllerBase
from ce1sus.brokers.event.eventbroker import EventBroker
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.staticbroker import TLPLevel, Risk, Analysis, Status
from datetime import datetime

class RestSearchController(RestControllerBase):

  MAX_LIMIT = 20
  PARAMETER_MAPPER = {'attribute':'viewAttributes',
                      'events':'viewEvents'}

  def __init__(self):
    RestControllerBase.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)

  def __getLimit(self, options):
    limit = options.get('limit', 20)

    # limit has to be between 0 and maximum value
    if limit < 0 or limit > RestSearchController.MAX_LIMIT:
      self.raiseError('InvalidArgument',
                      'The limit value has to be between 0 and 20')
    return limit

  def viewAttributes(self, uuid, apiKey, **options):
    try:
      withDefinition = options.get('Full-Definitions', False)
      startDate = options.get('startdate', None)
      endDate = options.get('enddate', datetime.now())
      offset = options.get('page', 0)
      limit = self.__getLimit(options)

      # serach on objecttype
      objectType = options.get('Object-Type', None)
      # with the following attribtes type + value
      objectAttribtues = options.get('Object-Attributes', list())
      # Filter on Attributes
      filterAttributes = options.get('attributes', list())

      filter = options.get('attributes', list())

      if objectType or objectAttribtues:
        valuesToLookFor = dict()

        for item in objectAttribtues:
          for key, value in item.iteritems():
            definition = self.attributeDefinitionBroker.getDefintionByName(key)
            # TODO: search inside textfield
            if definition.classIndex != 0:
              valuesToLookFor[value] = definition

        matchingAttributes = list()
        # find results
        for value, key in valuesToLookFor.iteritems():
          foundValues = self.attributeBroker.lookforAttributeValue(key,
                                                                 value,
                                                                 '==')
          matchingAttributes = matchingAttributes + foundValues

        result = list()
        for needle in matchingAttributes:
          try:
            event = needle.attribute.object.event
            if not event:
              event = self.eventBroker.getByID(needle.attribute.object.parentEvent_id)
            self._checkIfViewable(event, self.getUser(apiKey))

            restEvent = event.toRestObject(False)
            restObject = needle.attribute.object.toRestObject(False)



          except cherrypy.HTTPError:
            pass
        resultDict = {'Results': result}
        return self._returnMessage(resultDict)





      else:
        self.raiseError('InvalidArgument',
                         'At least one argument has to be specified')

    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def viewEvents(self, uuid, apiKey, **options):
    try:
      startDate = options.get('startdate', None)
      endDate = options.get('enddate', datetime.now())
      offset = options.get('page', 0)
      limit = self.__getLimit(options)


      # serach on objecttype
      objectType = options.get('Object-Type', None)
      # with the following attribtes type + value
      objectAttribtues = options.get('Object-Attributes', list())

      if objectType or objectAttribtues:
        # process needles
        valuesToLookFor = dict()

        for item in objectAttribtues:
          for key, value in item.iteritems():
            definition = self.attributeDefinitionBroker.getDefintionByName(key)
            # TODO: search inside textfield
            if definition.classIndex != 0:
              valuesToLookFor[value] = definition

        matchingAttributes = list()
        # find results
        for value, key in valuesToLookFor.iteritems():
          foundValues = self.attributeBroker.lookforAttributeValue(key,
                                                                 value,
                                                                 '==')
          matchingAttributes = matchingAttributes + foundValues

        result = list()
        for needle in matchingAttributes:
          try:
            event = needle.attribute.object.event
            if not event:
              event = self.eventBroker.getByID(needle.attribute.object.parentEvent_id)
            self._checkIfViewable(event, self.getUser(apiKey))
            result.append(event.uuid)
          except cherrypy.HTTPError:
            pass
        resultDict = {'Results': result}
        return self._returnMessage(resultDict)
      else:
        self.raiseError('InvalidArgument',
                         'At least one argument has to be specified')

    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def getFunctionName(self, parameter, action):
    if action == 'GET':
      return RestSearchController.PARAMETER_MAPPER.get(parameter, None)
    return None
