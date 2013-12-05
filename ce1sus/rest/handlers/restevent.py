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


class RestEventController(RestControllerBase):

  def __init__(self, sessionManager=None):
    RestControllerBase.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)

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
        event.bitValue.isRestInsert = True
        event.bitValue.isSharable = True
        # flush to DB
        self.eventBroker.insert(event, commit=False)

        event.objects = list()
        for obj in restEvent.objects:
          # create object
          dbObject = self.__convertRestObject(obj, event, event, commit=False)
          event.objects.append(dbObject)

        self.eventBroker.doCommit(True)

        return self._objectToJSON(event, showAll, withDefinition)

      except BrokerException as e:
        return self.raiseError('BrokerException', e)

    else:
      return self.raiseError('Exception', 'Not Implemented')

  def __convertRestObject(self, obj, parent, event, commit=False):
    dbObject = self._convertToObject(obj, parent, event, commit=commit)
    # generate Attributes
    dbObject.attributes = self._convertToAttribues(obj.attributes,
                                                          dbObject, commit)
    dbObject.children = list()
    for child in obj.children:
      childDBObj = self.__convertRestObject(child, dbObject, event, commit)
      dbObject.children.append(childDBObj)
    return dbObject
