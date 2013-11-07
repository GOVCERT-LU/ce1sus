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
from ce1sus.brokers.event.attributebroker import AttributeBroker
from dagr.db.broker import BrokerException, NothingFoundException
from ce1sus.brokers.event.objectbroker import ObjectBroker


class RestAttributeController(RestControllerBase):

  def __init__(self):
    RestControllerBase.__init__(self)
    self.attribtueBroker = self.brokerFactory(AttributeBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)

  @cherrypy.expose
  def view(self, identifier, apiKey, showAll=None, withDefinition=None):
    try:
      attribute = self.attribtueBroker.getByID(identifier)
      self._checkIfViewable(attribute.object.event, self.getUser(apiKey))
      return self._objectToJSON(attribute, showAll, withDefinition)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  @cherrypy.expose
  def delete(self, identifier, apiKey):
    try:
      attribute = self.attribtueBroker.getByID(identifier)
      self._checkIfViewable(attribute.object.event, self.getUser(apiKey))
      self.attribtueBroker.removeByID(attribute.identifier)
    except NothingFoundException as e:
      return self.raiseError('NothingFoundException', e)
    except BrokerException as e:
      return self.raiseError('BrokerException', e)

  # pylint: disable =R0913
  @cherrypy.expose
  def  update(self,
              identifier,
              apiKey,
              objectID=None,
              showAll=None,
              withDefinition=None):
    if identifier == '0':
      try:
        attribute = self.getPostObject()
        # create object
        if not objectID:
          return self.raiseError('BrokerException',
                                 ('No ID specified for object use objectID='
                                  + '(an id of an object)'))
        obj = self.objectBroker.getByID(objectID)

        if attribute.value != '(Not Provided)':
          attrDefinition = self._convertToAttributeDefinition(
                                                          attribute.definition,
                                                          obj.definition,
                                                          False)
          dbAttribute = self._createAttribute(attribute,
                                             attrDefinition,
                                             obj,
                                             False)
        obj.attributes.append(dbAttribute)

        self.objectBroker.doCommit(True)
        self.attributeBroker.doCommit(True)

        return self._objectToJSON(dbAttribute, showAll, withDefinition)

      except BrokerException as e:
        return self.raiseError('BrokerException', e)

    else:
      return self.raiseError('Exception', 'Not Implemented')
