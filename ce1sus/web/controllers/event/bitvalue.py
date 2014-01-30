# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Nov 19, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, requireReferer
from dagr.db.broker import BrokerException
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.event.eventbroker import EventBroker


class BitValueController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.eventBroker = self.brokerFactory(EventBroker)

  def __setBitValues(self, instance, share, validated='1'):
    if share == '1':
      instance.bitValue.isSharable = True
    else:
      instance.bitValue.isSharable = False
    if validated == '1':
      instance.bitValue.isValidated = True
    else:
      instance.bitValue.isValidated = False

  def __generateTemplate(self, eventID, instance, parentDisabled):
    template = self.getTemplate('/events/event/bitvalue/bitvalueModal.html')
    return self.cleanHTMLCode(template.render(identifier=instance.identifier,
                           bitValue=instance.bitValue,
                           eventID=eventID,
                           enabled=parentDisabled))

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def setObjectProperties(self, eventID, objectID):
    event = self.eventBroker.getByID(eventID)
    # right checks
    if not self.isEventOwner(self.event, self.getUser(True)):
      raise cherrypy.HTTPError(403)

    obj = self.objectBroker.getByID(objectID)
    return self.__generateTemplate(eventID, obj, True)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def modifyObjectProperties(self, eventID, identifier, shared):
    try:
      event = self.eventBroker.getByID(eventID)
      # right checks
      if not self.isEventOwner(self.event, self.getUser(True)):
        raise cherrypy.HTTPError(403)

      obj = self.objectBroker.getByID(identifier)
      self.__setBitValues(obj, shared)
      self.objectBroker.update(obj)
      return self.returnAjaxOK()
    except BrokerException as e:
      self.getLogger().debug(e)
      return '{0}'.format(e)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def setAttributeProperties(self, eventID, objectID, attributeID):
    event = self.eventBroker.getByID(eventID)
    # right checks
    if not self.isEventOwner(self.event, self.getUser(True)):
          raise cherrypy.HTTPError(403)

    attribute = self.attributeBroker.getByID(attributeID)
    obj = self.objectBroker.getByID(objectID)
    return self.__generateTemplate(eventID, attribute, obj.bitValue.isSharable)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def modifyAttributeProperties(self, eventID, identifier, shared='0'):
    try:
      event = self.eventBroker.getByID(eventID)
      # right checks
      if not self.isEventOwner(self.event, self.getUser(True)):
          raise cherrypy.HTTPError(403)
      attribute = self.attributeBroker.getByID(identifier)
      self.__setBitValues(attribute, shared)
      # Be careful not the values have to be updated!
      # Therefore the update function cannot be used for this!
      self.objectBroker.update(attribute)
      return self.returnAjaxOK()
    except BrokerException as e:
      self.getLogger().debug(e)
      return '{0}'.format(e)
