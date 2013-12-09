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
import json


class RestSearchController(RestControllerBase):

  MAX_LIMIT = 20
  PARAMETER_MAPPER = {'attributes':'viewAttributes',
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

  def getParentObject(self, event, obj, seenEvents):
    if not obj.parentObject_id:
      return None

    orgParentObj = self.objectBroker.getByID(obj.parentObject_id)
    if orgParentObj.bitValue.isValidated and orgParentObj.bitValue.isSharable:

      parentObject = seenEvents[event.identifier][1].get(orgParentObj.identifier, None)
      if not parentObject:
        # memorize parentObject
        parentObject = orgParentObj.toRestObject(False)
        seenEvents[event.identifier][1][orgParentObj.identifier] = parentObject
        if orgParentObj.parentObject_id:
          parentParentObject = seenEvents[event.identifier][1].get(orgParentObj.parentObject.identifier, None)
          if not parentParentObject:
            parentParentObject = self.getParentObject(event, orgParentObj, seenEvents)
            if parentParentObject:
              restParent = parentParentObject.toRestObject(False)
              seenEvents[event.identifier][1][orgParentObj.parentObject.identifier] = restParent
              parentObject.parent = restParent
            else:
              return None
          else:
            parentObject.parent = restParent

        else:
          restEvent = seenEvents[event.identifier][0]
          restEvent.objects.append(parentObject)

      return parentObject
    else:
      return None

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
        seenEvents = dict()
        for needle in matchingAttributes:
          if needle.attribute.bitValue.isValidated and needle.attribute.bitValue.isSharable:

            try:
              event = needle.attribute.object.event

              if not event:
                event = self.eventBroker.getByID(needle.attribute.object.parentEvent_id)
              self._checkIfViewable(event, self.getUser(apiKey))


              restEvent = seenEvents.get(event.identifier, None)
              if not restEvent:
                restEvent = event.toRestObject(False)
                seenEvents[event.identifier] = (restEvent, dict())
              else:
                restEvent = restEvent[0]
              # check if obj is accessible
              if needle.attribute.object.bitValue.isValidated and needle.attribute.object.bitValue.isSharable:
                restObject = seenEvents[event.identifier][1].get(needle.attribute.object.identifier, None)
                if not restObject:
                  obj = needle.attribute.object
                  restObject = obj.toRestObject(False)
                  if obj.parentObject_id is None:
                    restEvent.objects.append(restObject)
                  else:
                    parentObject = self.getParentObject(event, obj, seenEvents)
                    if parentObject:
                      parentObject.children.append(restObject)

                  seenEvents[event.identifier][1][obj.identifier] = restObject

                restAttribute = needle.attribute.toRestObject()
                restObject.attributes.append(restAttribute)

            except cherrypy.HTTPError:
              pass

        # make list of results
        result = list()
        for event, objs in seenEvents.itervalues():
          dictionary = dict(event.toJSON(full=True,
                             withDefinition=withDefinition).items()
                 )
          obj = json.dumps(dictionary)
          result.append(obj)

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
