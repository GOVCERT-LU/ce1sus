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

  def __checkIfBelongs(self, id, array):
    if array:
      return id in array
    else:
      return True

  def viewAttributes(self, uuid, apiKey, **options):
    try:
      withDefinition = options.get('Full-Definitions', False)
      startDate = options.get('startdate', None)
      endDate = options.get('enddate', datetime.now())
      offset = options.get('page', 0)
      limit = self.__getLimit(options)

      # object type to look foor
      performSearch = True
      objectNeedle = options.get('Object-Type', None)
      if objectNeedle:
        definition = self.objectDefinitionBroker.getDefintionByName(objectNeedle)
        # TODO: search inside textfield
      else:
        performSearch = False

      if performSearch:
        # object Attribues to look for
        needles = options.get('Object-Attributes', list())
        completeNeedles = dict()
        for needle in needles:
            for key, value in needle.iteritems():
              definition = self.attributeDefinitionBroker.getDefintionByName(key)
              if definition.classIndex != 0:
                completeNeedles[value] = definition
        if not completeNeedles:
          performSearch = False

      # Desired Return Attibutes
      if performSearch:
        requestedAttributes = list()
        for item in options.get('attributes', list()):
          definition = self.attributeDefinitionBroker.getDefintionByName(item)
          requestedAttributes.append(definition.identifier)

          # Note if no requested attribues are defined return all for the object having the needle

      if performSearch:

        # find Matching attribtues
        matchingAttributes = list()
        for definition, needle in completeNeedles.iteritems():
          foundValues = self.attributeBroker.lookforAttributeValue(needle,
                                                                 definition,
                                                                 '==')
          matchingAttributes = matchingAttributes + foundValues

        # cache
        seenItems = dict()

        for item in matchingAttributes:
          attribute = item.attribute
          # check if attribute is sharable and validated
          if attribute.bitValue.isValidated and attribute.bitValue.isSharable:
            # check it is one of the requested attributes
            obj = attribute.object
             # check if object is sharable and validated
            if obj.bitValue.isValidated and obj.bitValue.isSharable:
              if requestedAttributes:
                # append only the requested attributes
                neededAttributes = list()
                for item in obj.attributes:
                  if item.def_attribute_id in requestedAttributes:
                    neededAttributes.append(item)
              else:
                # append all attributes
                neededAttributes = obj.attributes

              # get the event
              event = obj.event
              if not event:
                event = self.eventBroker.getByID(obj.parentEvent_id)

              try:
                # check if the event can be accessed
                self._checkIfViewable(event, self.getUser(apiKey))

                # get rest from cache
                restEvent = seenItems.get(event.identifier, None)
                if not restEvent:
                  # if not cached put it there
                  restEvent = event.toRestObject(False)
                  seenItems[event.identifier] = (restEvent, dict())
                else:
                  # get it from cache
                  restEvent = restEvent[0]

                # get obj from cache
                restObject = seenItems[event.identifier][1].get(obj.identifier, None)
                if not restObject:
                  restObject = obj.toRestObject(False)
                  if obj.parentObject_id is None:
                    restEvent.objects.append(restObject)
                  else:
                    parentObject = self.getParentObject(event, obj, seenItems)
                    if parentObject:
                      parentObject.children.append(restObject)


                  # append required attributes to the object
                  for item in neededAttributes:
                    restObject.attributes.append(item.toRestObject())

                  seenItems[event.identifier][1][obj.identifier] = restObject

              except cherrypy.HTTPError:
                # Do nothing if the user cant see the event
                pass

            # make list of results

        result = list()
        if performSearch:

          for event, objs in seenItems.itervalues():
            dictionary = dict(event.toJSON(full=True,
                               withDefinition=withDefinition).items()
                   )
            obj = json.dumps(dictionary)
            result.append(obj)

        resultDict = {'Results': result}
        return self._returnMessage(resultDict)


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
