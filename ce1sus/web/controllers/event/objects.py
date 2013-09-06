# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.web.controllers.base import BaseController
import cherrypy
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from datetime import datetime
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, Object
from ce1sus.brokers.definitionbroker import ObjectDefinitionBroker, \
                  AttributeDefinitionBroker
from ce1sus.web.helpers.protection import require, requireReferer
from dagr.db.broker import ValidationException, \
BrokerException

class ObjectsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.def_objectBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def objects(self, eventID, objectID=None):
    """
     renders the file with the base layout of the main object page

    :param objectID: the identifier of the object (only set if the details
                     should be displayed of this object)
    :type objectID: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/objects/objectsBase.html')
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)

    # if event has objects

    labels = [{'identifier':'#'},
              {'key':'Type'},
              {'value':'Value'}]
    # mako will append the missing url part
    paginatorOptions = PaginatorOptions(('/events/event/objects/'
                                         + 'objects/{0}/%(objectID)s/').format(
                                                                      eventID),
                                      'eventTabs{0}TabContent'.format(eventID))
    # mako will append the missing url part
    paginatorOptions.addOption('MODAL',
                               'VIEW',
                               ('/events/event/attribute/'
                                + 'view/{0}/%(objectID)s/').format(eventID),
                               modalTitle='View Attribute')
    # mako will append the missing url part
    paginatorOptions.addOption('DIALOG',
                               'REMOVE',
                               ('/events/event/attribute/modifyAttribute?'
                                + 'action=remove&eventID={0}&objectID'
                                + '=%(objectID)s&attributeID=').format(eventID),
                               refresh=True)
    # will be associated in the view!!! only to keep it simple!
    paginator = Paginator(items=list(),
                          labelsAndProperty=labels,
                          paginatorOptions=paginatorOptions)
    # fill dictionary of attribute definitions but only the needed ones


    try:
      for obj in event.objects:
        cbAttributeDefintiionsDict = self.def_attributesBroker.getCBValues(
                                                      obj.definition.identifier)
    except BrokerException:
      cbAttributeDefintiionsDict = dict()



    return template.render(eventID=eventID,
                           objectList=event.objects,
                           cbObjDefinitions=self.def_objectBroker.getCBValues(),
                          cbAttributeDefintiionsDict=cbAttributeDefintiionsDict,
                           paginator=paginator,
                           objectID=objectID)


  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def addObject(self, eventID):
    """
     renders the file for displaying the add an attribute form

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)
    template = self.getTemplate('/events/event/objects/objectModal.html')
    cbObjDefinitions = self.def_objectBroker.getCBValues()
    return template.render(cbObjDefinitions=cbObjDefinitions,
                           eventID=eventID,
                           object=None,
                           errorMsg=None)
  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def addChildObject(self, eventID, objectID):
    """
    renders the add an object page

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)
    template = self.getTemplate('/events/event/objects/childObjectModal.html')
    cbObjDefinitions = self.def_objectBroker.getCBValues()
    return template.render(cbObjDefinitions=cbObjDefinitions,
                           eventID=eventID,
                           object=None,
                           objectID=objectID,
                           errorMsg=None)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def attachObject(self, eventID=None, definition=None):
    """
    Inserts an an event object.

    :param identifier: The identifier of the event
    :type identifier: Integer
    :param definition: The identifier of the definition associated to the object
    :type definition: Integer

    :returns: generated HTML
    """
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)
    # Here is an insertion only so the action parameter is not needed, btw.
    # the object has no real editable values since if the definition would
    # change also the attributes have to change as some might be incompatible!!
    obj = Object()
    obj.identifier = None
    obj.def_object_id = definition
    obj.definition = self.def_objectBroker.getByID(obj.def_object_id)
    obj.created = datetime.now()
    obj.event_id = eventID
    obj.event = event
    obj.creator_id = self.getUser().identifier
    errors = False
    errorMsg = None
    try:
      self.objectBroker.insert(obj)
      # TODO: update event
      # self.updateEvent(event)
      obj = None
    except ValidationException:
      self.getLogger().debug('Event is invalid')
      errors = True
    except BrokerException as e:
      self.getLogger().critical(e)
      errorMsg = 'An unexpected error occured: {0}'.format(e)
      errors = True
    if errors:
      template = self.getTemplate('/events/event/objects/objectModal.html')
      cbObjDefinitions = self.def_objectBroker.getCBValues()
      return template.render(cbObjDefinitions=cbObjDefinitions,
                             eventID=eventID,
                             object=obj,
                             errorMsg=errorMsg)
    else:
      # ok everything went right
      return self.returnAjaxOK()

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def attachChildObject(self, objectID=None, eventID=None, definition=None):
    """
    Inserts an an event object.

    :param identifier: The identifier of the event
    :type identifier: Integer
    :param definition: The identifier of the definition associated to the object
    :type definition: Integer

    :returns: generated HTML
    """
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)
    # Here is an insertion only so the action parameter is not needed, btw.
    # the object has no real editable values since if the definition would
    # change also the attributes have to change as some might be incompatible!!

    obj = Object()
    obj.identifier = None
    obj.def_object_id = definition
    obj.definition = self.def_objectBroker.getByID(obj.def_object_id)
    obj.created = datetime.now()
    obj.event_id = None
    obj.event = None
    obj.parentObject_id = objectID
    obj.creator_id = self.getUser().identifier
    errors = False
    errorMsg = None
    try:
      self.objectBroker.insert(obj)
      # TODO: update event
      # self.updateEvent(event)
      obj = None
    except ValidationException:
      self.getLogger().debug('Event is invalid')
      errors = True
    except BrokerException as e:
      self.getLogger().critical(e)
      errorMsg = 'An unexpected error occured: {0}'.format(e)
      errors = True
    if errors:
      template = self.getTemplate('/events/event/objects/objectModal.html')
      cbObjDefinitions = self.def_objectBroker.getCBValues()
      return template.render(cbObjDefinitions=cbObjDefinitions,
                             eventID=None,
                             object=obj,
                             errorMsg=errorMsg)
    else:
      # ok everything went right
      return self.returnAjaxOK()

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def removeObject(self, eventID=None, objectID=None):
    """
    Removes an object
    """
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event.groups, self.getUser().identifier ==
                         event.creator.identifier)
    # remove object
    errors = False
    try:
      self.objectBroker.removeByID(objectID)
    except BrokerException as e:
      self.getLogger().critical(e)
      errors = True
    if errors:
      return 'Et ass einfach net gangen'
    else:
      return self.returnAjaxOK()
