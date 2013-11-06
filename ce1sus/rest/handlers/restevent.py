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
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.event.attributebroker import AttributeBroker, Attribute
from ce1sus.brokers.event.eventclasses import Object, Event
from ce1sus.brokers.definition.definitionclasses import AttributeDefinition, \
                                                        ObjectDefinition
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                      AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                                                        ObjectDefinitionBroker
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.staticbroker import TLPLevel, Risk, Analysis, Status
import json
from datetime import datetime
from dagr.helpers.converters import ObjectConverter

class RestEventController(RestControllerBase):

  def __init__(self, sessionManager=None):
    RestControllerBase.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.objectDefinitionBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.attributeDefinitionBroker = self.brokerFactory(AttributeDefinitionBroker)
  @cherrypy.expose
  def view(self, identifier, apiKey, showAll=None, withDefinition=None):
    try:
      event = self.eventBroker.getEventForUser(identifier,
                                               self.getUser(apiKey))
      return self.objectToJSON(event, showAll, withDefinition)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)


  @cherrypy.expose
  def delete(self, identifier, apiKey):
    try:
      event = self.eventBroker.getEventForUser(identifier,
                                               self.getUser(apiKey))
      self.eventBroker.removeByID(event.identifier)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  def __convertToAttributeDefinition(self,
                                     restAttributeDefinition,
                                     objectDefinition,
                                     commit=False):
    # get definition if existing
      try:
        attrDefinition = self.attributeDefinitionBroker.getDefintionByCHKSUM(
                                                restAttributeDefinition.chksum
                                                                            )
      except NothingFoundException:
        # definition does not exist create one
        attrDefinition = AttributeDefinition()
        attrDefinition.name = restAttributeDefinition.name
        attrDefinition.description = restAttributeDefinition.description
        attrDefinition.regex = restAttributeDefinition.regex
        attrDefinition.classIndex = restAttributeDefinition.classIndex
        attrDefinition.handlerIndex = 0
        attrDefinition.deletable = 1
        attrDefinition.share = 1
        attrDefinition.relation = restAttributeDefinition.relation
        self.attributeDefinitionBroker.insert(attrDefinition, commit=False)

        # update objectRelations as the attribute was not set
        objectDefinition.attributes.append(attrDefinition)
        self.objectBroker.update(objDefinition, commit=False)

        self.doCommit(commit)

      return attrDefinition


  def __createAttribute(self,
                        restAttribute,
                        attributeDefinition,
                        object,
                        commit=False):

    user = object.creator

    # create the actual attribute
    dbAttribute = Attribute()
    dbAttribute.identifier = None
    dbAttribute.value = restAttribute.value
    dbAttribute.object = object
    dbAttribute.object_id = object.identifier
    dbAttribute.def_attribute_id = attributeDefinition.identifier
    dbAttribute.definition = attributeDefinition
    dbAttribute.created = datetime.now()
    dbAttribute.modified = datetime.now()
    dbAttribute.creator = user
    dbAttribute.creator_id = user.identifier
    dbAttribute.modifier_id = user.identifier
    dbAttribute.modifier = user
    ObjectConverter.setInteger(dbAttribute,
                               'ioc',
                               restAttribute.ioc)

    self.attributeBroker.insert(dbAttribute, commit=False)

    return dbAttribute

  def __convertToAttribues(self, restAttributes, object, commit=False):

    result = list()
    for attribute in restAttributes:

      attrDefinition = self.__convertToAttributeDefinition(attribute.definition,
                                                           object.definition,
                                                           False)
      dbAttribute = self.__createAttribute(attribute,
                                           attrDefinition,
                                           object,
                                           False)
      result.append(dbAttribute)
    self.attributeBroker.doCommit(commit)
    return result

  def __convertToObjectDefinition(self, restObjectDefinition, commit=False):
    # create object

    # get definition if existing
    try:
      objDefinition = self.objectDefinitionBroker.getDefintionByCHKSUM(
                                                    restObjectDefinition.chksum
                                                                      )
    except NothingFoundException:
      objDefinition = ObjectDefinition()
      objDefinition.name = restObjectDefinition.name
      objDefinition.description = restObjectDefinition.description
      self.objectDefinitionBroker.insert(objDefinition, commit=commit)

    return objDefinition

  def __convertToObject(self, restObject, event, commit=False):
    objectDefinition = self.__convertToObjectDefinition(restObject.definition,
                                                        commit)
    user = event.creator

    if restObject.parentObject_id is None:
      dbObject = self.objectBroker.buildObject(None,
                                               event,
                                               objectDefinition,
                                               user,
                                               None)
    else:
      dbObject = self.objectBroker.buildObject(None,
                                               None,
                                               objectDefinition,
                                               user,
                                               restObject.parentObject_id)
    # flush to DB
    self.objectBroker.insert(dbObject, commit=False)

    return dbObject

  @cherrypy.expose
  def update(self, identifier, apiKey, showAll=None, withDefinition=None):
    if identifier == '0':
      try:
        restEvent = self.getPostObject()
        # map restEvent on event
        status = Status.getByName(restEvent.status)
        tlp_idx = TLPLevel.getByName(restEvent.tlp)
        risk = Risk.getByName(restEvent.risk)
        analysis = Analysis.getByName(restEvent.analysis)
        user = self.getUser(apiKey)
        event = self.eventBroker.buildEvent(
                       None,
                       'insert',
                       status,
                       tlp_idx,
                       restEvent.description,
                       restEvent.title,
                       restEvent.published,
                       restEvent.first_seen,
                       restEvent.last_seen,
                       risk,
                       analysis,
                       user)
        # flush to DB
        self.eventBroker.insert(event, commit=False)

        objs = list()
        for obj in restEvent.objects:
          # create object

          dbObject = self.__convertToObject(obj, event, commit=False)
          dbObject.attributes = self.__convertToAttribues(obj.attributes,
                                                          dbObject)
          objs.append(dbObject)

        event.objects = objs
        self.eventBroker.doCommit(True)
        self.objectBroker.doCommit(True)
        self.attributeBroker.doCommit(True)

        return self.objectToJSON(event, showAll, withDefinition)


      except BrokerException as e:
        return self.raiseError('BrokerException', e)

    else:
      return self.raiseError('Exception', 'Not Implemented')

