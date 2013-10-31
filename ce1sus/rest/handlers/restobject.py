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

  def __getObject(self, identifier, apiKey):
    obj = self.objectBroker.getByID(identifier)
    event = self.eventBroker.getEventForUser(obj.event.identifier,
                                               self.getUser(apiKey))
    del event
    return obj

  @cherrypy.expose
  def view(self, identifier, apiKey, showAll=None, withDefinition=None):
    try:
      obj = self.__getObject(identifier, apiKey)
      return self.objectToJSON(obj, showAll, withDefinition)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  @cherrypy.expose
  def delete(self, identifier, apiKey):
    try:
      obj = self.__getObject(identifier, apiKey)
      self.objectBroker.removeByID(obj.identifier)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  @cherrypy.expose
  def update(self, identifier, options):
    return self.raiseError('Exception', 'Not Implemented')

  @cherrypy.expose
  def insert(self, identifier, apiKey, options):
    return self.raiseError('Exception', 'Not Implemented')
