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
import json

class RestEventController(RestControllerBase):

  def __init__(self, sessionManager=None):
    RestControllerBase.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)

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

  @cherrypy.expose
  def update(self, identifier, apiKey, showAll=None, withDefinition=None):
    if identifier == '0':
      restEvent = self.getPostObject()
      # map restEvent on event
      status = Status.getByName(restEvent.status)
      tlp_idx = TLPLevel.getByName(restEvent.tlp)
      risk = Risk.getByName(restEvent.risk)
      analysis = Analysis.getByName(restEvent.analysis)
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
                     self.getUser(apiKey))
      # TODO: Attach objects
      # TODO: Attach attribtues
      self.eventBroker.insert(event)
      id = event.identifier
      eventResult = self.eventBroker.getByID()
      return self.objectToJSON(eventResult, showAll, withDefinition)
    else:
      return self.raiseError('Exception', 'Not Implemented')

