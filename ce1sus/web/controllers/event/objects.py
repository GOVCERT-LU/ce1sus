"""module holding all controllers needed for the event handling"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import copy
from framework.web.controllers.base import BaseController
import cherrypy
from framework.web.helpers.pagination import Paginator, PaginatorOptions
from datetime import datetime
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, \
                  AttributeBroker, Event, Object, Attribute, Comment, \
                  CommentBroker, Ticket, TicketBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel
from ce1sus.brokers.definitionbroker import ObjectDefinitionBroker, \
                  AttributeDefinitionBroker, AttributeDefinition
from ce1sus.web.helpers.protection import require
from cherrypy._cperror import HTTPRedirect
from framework.helpers.rt import RTHelper
import types
from framework.db.broker import NothingFoundException, ValidationException, \
BrokerException
from framework.helpers.converters import ObjectConverter
from ce1sus.web.helpers.protection import privileged
class ObjectsController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.def_objectBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)
    self.commentBroker = self.brokerFactory(CommentBroker)
    self.ticketBroker = self.brokerFactory(TicketBroker)

  @cherrypy.expose
  @require()
  def objects(self, eventID, objectID=None):
    template = self.getTemplate('/events/event/objects/objectsBase.html')
    return template.render(eventID=eventID,
                           objectID=objectID)

  @cherrypy.expose
  @require()
  def all(self, eventID):
    template = self.getTemplate('/events/event/objects/allObjects.html')
    event = self.eventBroker.getByID(eventID)

    # TODO imporve -> objectBroker get objects by event id
    return template.render(eventID=eventID,
                           objectList=event.objects,
                           cbObjDefinitions=self.def_objectBroker.getCBValues()
                           )

  @cherrypy.expose
  @require()
  def detail(self, eventID, objectID):
    template = self.getTemplate('/events/event/objects/details.html')

    labels = [{'identifier':'#'},
              {'key':'Type'},
              {'value':'Value'},
              {'creator.username':'Creator'},
              {'created':'CreatedOn'}]

    paginatorOptions = PaginatorOptions('/events/event/objects/detail/{0}/{1}'.format(eventID, objectID), 'objectRight')
    paginatorOptions.addOption('MODAL', 'VIEW', '/events/event/attribute/view/{0}/{1}/'.format(eventID, objectID), modalTitle='View Attribute')
    paginatorOptions.addOption('MODAL', 'EDIT', '/events/event/attribute/edit/{0}/{1}/'.format(eventID, objectID), modalTitle='Edit Attribute', postUrl='/events/event/attribute/modifyAttribute', refresh=True)
    paginatorOptions.addOption('DIALOG', 'REMOVE', '/events/event/attribute/modifyAttribute?action=remove&eventID={0}&objectID={1}&attributeID='.format(eventID, objectID), refresh=True)


    # will be associated in the view!!! only to keep it simple!
    paginator = Paginator(items=list(),
                          labelsAndProperty=labels,
                          paginatorOptions=paginatorOptions)

    # fill dictionary of attribute definitions but only the needed ones

    objectList = list()
    try:
      obj = self.objectBroker.getByID(objectID)
      cbAttributeDefintiionsDict = self.def_attributesBroker.getCBValues(
                                                      obj.definition.identifier)
    except Exception:
      obj = None
      cbAttributeDefintiionsDict = dict()

    objectList.append(obj)




    cbObjDefinitions = self.def_objectBroker.getCBValues()

    return template.render(eventID=eventID,
                           cbObjDefinitions=cbObjDefinitions,
                           cbAttributeDefintiionsDict=cbAttributeDefintiionsDict,
                           paginator=paginator,
                           object=obj)


  @require(privileged())
  @cherrypy.expose
  def addObject(self, eventID):
    template = self.getTemplate('/events/event/objects/objectModal.html')
    cbObjDefinitions = self.def_objectBroker.getCBValues()
    return template.render(cbObjDefinitions=cbObjDefinitions,
                           eventID=eventID,
                           object=None,
                           errorMsg=None)

  @cherrypy.expose
  @require()
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
    obj.user_id = self.getUser().identifier
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
  @require()
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
