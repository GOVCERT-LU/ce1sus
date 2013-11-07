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
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.definition.attributedefinitionbroker import \
                                                      AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                                                        ObjectDefinitionBroker
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.staticbroker import TLPLevel, Risk, Analysis, Status


class RestEventController(RestControllerBase):

  def __init__(self, sessionManager=None):
    RestControllerBase.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.objectDefinitionBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.attributeDefinitionBroker = self.brokerFactory(
                                                    AttributeDefinitionBroker
                                                       )

  @cherrypy.expose
  def view(self, identifier, apiKey, showAll=None, withDefinition=None):
    try:
      event = self.eventBroker.getByID(identifier)
      self._checkIfViewable(event, self.getUser(apiKey))
      return self._objectToJSON(event, showAll, withDefinition)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  @cherrypy.expose
  def delete(self, identifier, apiKey):
    try:
      event = self.eventBroker.getByID(identifier)
      self._checkIfViewable(event, self.getUser(apiKey))
      self.eventBroker.removeByID(event.identifier)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  @cherrypy.expose
  def update(self, identifier, apiKey, showAll=None, withDefinition=None):
    if identifier == '0':
      try:
        restEvent = self.getPostObject()
        # map restEvent on event
        user = self.getUser(apiKey)
        event = self.eventBroker.buildEvent(
                       None,
                       'insert',
                       Status.getByName(restEvent.status),
                       TLPLevel.getByName(restEvent.tlp),
                       restEvent.description,
                       restEvent.title,
                       restEvent.published,
                       restEvent.first_seen,
                       restEvent.last_seen,
                       Risk.getByName(restEvent.risk),
                       Analysis.getByName(restEvent.analysis),
                       user)
        # flush to DB
        self.eventBroker.insert(event, commit=False)

        objs = list()
        for obj in restEvent.objects:
          # create object

          dbObject = self._convertToObject(obj, event, commit=False)
          dbObject.attributes = self._convertToAttribues(obj.attributes,
                                                          dbObject)
          objs.append(dbObject)

        event.objects = objs
        self.eventBroker.doCommit(True)
        self.objectBroker.doCommit(True)
        self.attributeBroker.doCommit(True)

        return self._objectToJSON(event, showAll, withDefinition)

      except BrokerException as e:
        return self.raiseError('BrokerException', e)

    else:
      return self.raiseError('Exception', 'Not Implemented')
