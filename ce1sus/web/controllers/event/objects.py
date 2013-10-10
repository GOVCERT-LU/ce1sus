# -*- coding: utf-8 -*-

"""
module handing the obejcts pages

Created: Aug, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from ce1sus.brokers.definition.objectdefinitionbroker import \
                  ObjectDefinitionBroker
from ce1sus.brokers.definition.attributedefinitionbroker import \
                  AttributeDefinitionBroker
from ce1sus.web.helpers.protection import require, requireReferer
from dagr.db.broker import ValidationException, \
BrokerException
import dagr.helpers.string as string
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker


class ObjectsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
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
    self.checkIfViewable(event)

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
      if len(event.objects) > 0:
        for obj in event.objects:
          cbAttributeDefintiionsDict = self.def_attributesBroker.getCBValues(
                                                    obj.definition.identifier)
      else:
        cbAttributeDefintiionsDict = dict()
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
    self.checkIfViewable(event)
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
    self.checkIfViewable(event)
    template = self.getTemplate('/events/event/objects/childObjectModal.html')
    cbObjDefinitions = self.def_objectBroker.getCBValues()
    return template.render(cbObjDefinitions=cbObjDefinitions,
                           eventID=eventID,
                           object=None,
                           objectID=objectID,
                           errorMsg=None)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def attachObject(self, eventID, definition=None):
    """
    Inserts an an event object.

    :param identifier: The identifier of the event
    :type identifier: Integer
    :param definition: The identifier of the definition associated to the
                       object
    :type definition: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/objects/objectModal.html')
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event)
    # Here is an insertion only so the action parameter is not needed, btw.
    # the object has no real editable values since if the definition would
    # change also the attributes have to change as some might be incompatible!!
    definition = self.def_objectBroker.getByID(definition)
    obj = self.objectBroker.buildObject(None,
                                        event,
                                      definition,
                                      self.getUser())
    try:
      self.objectBroker.insert(obj, False)
      # update last seen etc of event
      self.eventBroker.updateLastSeen(event, self.getUser(), False)
      self.eventBroker.doCommit(True)

      return self.returnAjaxOK()
    except ValidationException:
      self.getLogger().debug('Event is invalid')
      return template.render(object=obj,
                          cbObjDefinitions=self.def_objectBroker.getCBValues(),
                             eventID=eventID)
    except BrokerException as e:
      self.getLogger().error(e)
      return 'An unexpected error occured: {0}'.format(e)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def attachChildObject(self, objectID=None, eventID=None, definition=None):
    """
    Inserts an an event object.

    :param identifier: The identifier of the event
    :type identifier: Integer
    :param definition: The identifier of the definition associated to the
                       object
    :type definition: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/objects/objectModal.html')
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event)
    # Here is an insertion only so the action parameter is not needed, btw.
    # the object has no real editable values since if the definition would
    # change also the attributes have to change as some might be incompatible!!

    obj = self.objectBroker.buildObject(None,
                                  None,
                                  self.def_objectBroker.getByID(definition),
                                  self.getUser(),
                                  objectID)
    try:
      self.objectBroker.insert(obj, False)
      # update last seen etc of event
      self.eventBroker.updateLastSeen(event, self.getUser(), False)
      self.eventBroker.doCommit(True)
      return self.returnAjaxOK()
    except ValidationException:
      self.getLogger().debug('Event is invalid')
      return template.render(eventID=eventID,
                          cbObjDefinitions=self.def_objectBroker.getCBValues(),
                             object=obj)
    except BrokerException as e:
      self.getLogger().critical(e)
      return 'An unexpected error occured: {0}'.format(e)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def removeObject(self, eventID=None, objectID=None):
    """
    Removes an object
    """
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event)
    # remove object
    try:
      self.objectBroker.removeByID(objectID)
      return self.returnAjaxOK()
    except BrokerException as e:
      self.getLogger().critical(e)
      return '{0}'.format(e)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def setObjectParent(self, eventID, objectID):
    """
    Renders page for setting the relations between objects,objects and events

    :param identifier: The identifier of the event
    :type identifier: Integer
    :param definition: The identifier of the definition associated to the
                       object
    :type definition: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/events/event/objects/parentModal.html')
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event)

    # get concerned object
    obj = self.objectBroker.getByID(objectID)

    if obj.event_id:
      isEventParent = True
      selected = None
    else:
      isEventParent = False
      selected = obj.parentObject_id
    eventChildren = self.objectBroker.getCDValuesObjectParents(eventID,
                                                               obj.identifier)
    # prepare CBArray
    cbValues = dict()
    for child in eventChildren:
      key = '{0} - {1}'.format(child.definition.name, child.identifier)
      cbValues[key] = child.identifier
    return template.render(eventID=eventID,
                           objectID=objectID,
                           cbValues=cbValues,
                           isEventParent=isEventParent,
                           selected=selected)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def modifyParentRelation(self,
                           eventID,
                           objectID,
                           parentObjectID=None,
                           setEventParent=None):
    """
    modifies the relations between objects,objects and events
    """
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event)
    if setEventParent is None and not string.isNotNull(parentObjectID):
      return 'Please select someting before saving.'
    obj = self.objectBroker.getByID(objectID)
    if setEventParent is None:
      obj.event_id = None
      obj.event = None
      obj.parentObject_id = parentObjectID
      self.objectBroker.update(obj)
    else:
      obj.event_id = eventID
      obj.event = event
      obj.parentObject_id = None
      self.objectBroker.update(obj)

    return self.returnAjaxOK()
