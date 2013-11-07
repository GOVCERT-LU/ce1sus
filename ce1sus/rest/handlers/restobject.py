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
from dagr.db.broker import BrokerException, NothingFoundException


class RestObjectController(RestControllerBase):

  def __init__(self, sessionManager=None):
    RestControllerBase.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)

  @cherrypy.expose
  def view(self, identifier, apiKey, showAll=None, withDefinition=None):
    try:
      obj = self.objectBroker.getByID(identifier)
      self._checkIfViewable(obj.event, self.getUser(apiKey))
      return self._objectToJSON(obj, showAll, withDefinition)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  @cherrypy.expose
  def delete(self, identifier, apiKey):
    try:
      obj = self.objectBroker.getByID(identifier)
      self._checkIfViewable(obj.event, self.getUser(apiKey))
      self.objectBroker.removeByID(obj.identifier)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  # pylint: disable =R0913
  @cherrypy.expose
  def  update(self,
              identifier,
              apiKey,
              eventUUID=None,
              showAll=None,
              withDefinition=None):
    if identifier == '0':
      try:
        obj = self.getPostObject()
        # create object
        if not eventUUID:
          return self.raiseError('BrokerException',
                                 ('No UUID specified for event use eventUUUID='
                                  + '(a UUID)'))
        event = self.eventBroker.getByUUID(eventUUID)

        dbObject = self._convertToObject(obj, event, commit=False)
        dbObject.attributes = self._convertToAttribues(obj.attributes,
                                                          dbObject)

        self.objectBroker.doCommit(True)
        self.attributeBroker.doCommit(True)

        return self._objectToJSON(dbObject, showAll, withDefinition)

      except BrokerException as e:
        return self.raiseError('BrokerException', e)

    else:
      return self.raiseError('Exception', 'Not Implemented')
