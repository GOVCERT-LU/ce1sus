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


class RestEventController(RestControllerBase):

  def __init__(self):
    self.eventBroker = self.brokerFactory(EventBroker)

  @cherrypy.expose
  def view(self, identifier, apiKey, showAll=None):
    try:
      event = self.eventBroker.getEventForUser(identifier,
                                               self.getUser(apiKey))
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)
    return self.objectToJSON(event, showAll)

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
  def update(self, identifier, options):
    return self.raiseError('Exception', 'Not Implemented')

  @cherrypy.expose
  def add(self, identifier, apiKey, options):
    return self.raiseError('Exception', 'Not Implemented')
