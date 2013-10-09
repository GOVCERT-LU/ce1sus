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
from ce1sus.brokers.event.attributebroker import AttributeBroker
from dagr.db.broker import BrokerException, NothingFoundException


class RestAttributeController(RestControllerBase):

  def __init__(self):
    self.eventBroker = self.brokerFactory(EventBroker)
    self.attribtueBroker = self.brokerFactory(AttributeBroker)

  def __getAttribute(self, identifier, apiKey):
    attribute = self.attribtueBroker.getByID(identifier)
    event = self.eventBroker.getEventForUser(attribute.object.event.identifier,
                                               self.getUser(apiKey))
    return attribute

  @cherrypy.expose
  def view(self, identifier, apiKey, showAll=None):
    try:
      attribute = self.__getAttribute(identifier, apiKey)
      return self.objectToJSON(attribute, showAll)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  @cherrypy.expose
  def delete(self, identifier, apiKey):
    try:
      attribute = self.__getAttribute(identifier, apiKey)
      self.attribtueBroker.removeByID(attribute.identifier)
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
