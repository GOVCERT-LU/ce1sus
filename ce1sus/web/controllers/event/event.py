# -*- coding: utf-8 -*-

"""
module handing the event pages

Created: Aug 28, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'"""module holding all controllers needed for
                        the event handling"""

from dagr.web.controllers.base import BaseController
import cherrypy
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, \
                  AttributeBroker, Event, CommentBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from ce1sus.brokers.definitionbroker import ObjectDefinitionBroker, \
                  AttributeDefinitionBroker
from ce1sus.web.helpers.protection import require, requireReferer
from dagr.db.broker import ValidationException, BrokerException


# pylint: disable=R0903,R0902
class Relation(object):
  """
  Relation container used for displaying the relations
  """
  def __init__(self):
    self.identifier = 0
    self.eventID = 0
    self.eventName = 0
    self.objectID = 0
    self.objectName = 0
    self.attributeID = 0
    self.attributeName = 0
    self.attributeValue = 0

class EventController(BaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    BaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.def_objectBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)
    self.commentBroker = self.brokerFactory(CommentBroker)

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def view(self, eventID):
    """
    renders the base page for displaying events

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)
    template = self.mako.getTemplate('/events/event/eventBase.html')
    return template.render(eventID=eventID)

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def event(self, eventID):
    """
    renders the event page for displaying a single event

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/event/view.html')
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier ==
                         event.creator.identifier)

    objectLabels = [{'identifier':'#'},
              {'definition.name':'Type'},
              {'creator.username':'Created by'},
              {'created':'CreatedOn'}]
    paginatorOptions = PaginatorOptions('/events/recent',
                                        'eventsTabTabContent')
    paginatorOptions.addOption('TAB',
                          'VIEW',
                          '/events/event/objects/objects/{0}'.format(eventID),
                          contentid='',
                          tabid='eventObjects{0}'.format(eventID))
    objectPaginator = Paginator(items=event.objects,
                          labelsAndProperty=objectLabels,
                          paginatorOptions=paginatorOptions)
    objectPaginator.itemsPerPage = 3

    relationLabels = [{'eventID':'Event #'},
                      {'eventName':'Event Name'},
              {'objectID':'Object #'},
              {'objectName':'Object Name'},
              {'attributeID':'Attribute #'},
              {'attributeName':'Attribute Name'},
              {'attributeValue':'Attribute Value'}]
    result = list()
    try:
      # get for each object
      relations = self.__getRelationsObjects(event.objects)
      # prepare list
      for relation in relations:
        temp = Relation()
        if relation.sameAttribute.object.event is None:
          event = self.eventBroker.getEventByObjectID(relation
                                              .sameAttribute.object
                                              .parentObject_id)
        else:
          event = relation.sameAttribute.object.event
        temp.eventID = event.identifier
        temp.identifier = event.identifier
        temp.eventName = event.title
        temp.objectID = relation.sameAttribute.object.identifier
        temp.objectName = relation.sameAttribute.object.definition.name
        temp.attributeID = relation.sameAttribute.identifier
        temp.attributeName = relation.sameAttribute.definition.name
        temp.attributeValue = relation.sameAttribute.value
        result.append(temp)
    except BrokerException:
      pass

    relationsPaginatorOptions = PaginatorOptions('/events/recent',
                                                 'eventsTabTabContent')
    relationsPaginatorOptions.addOption('NEWTAB',
                               'VIEW',
                               '/events/event/view/',
                               contentid='')

    relationPaginator = Paginator(items=result,
                          labelsAndProperty=relationLabels,
                          paginatorOptions=relationsPaginatorOptions)
    relationPaginator.itemsPerPage = 3

    return template.render(objectPaginator=objectPaginator,
                           relationPaginator=relationPaginator,
                           event=event,
                           cbStatusValues=Status.getDefinitions(),
                           cbTLPValues=TLPLevel.getDefinitions(),
                           comments=event.comments,
                           cbAnalysisValues=Analysis.getDefinitions(),
                           cbRiskValues=Risk.getDefinitions())

  def __getRelationsObjects(self, objects):
    """
    Returns the relation of the given objects

    :param objects: list of Objects
    :type objects: List of Objects

    :returns: List of Relations
    """
    result = list()
    for obj in objects:
      result = result + self.__getRelationsObject(obj)
    return result

  def __getRelationsObject(self, obj):
    """
    Returns the relation of the given object

    :param objects: Object to find the relation
    :type objects: Objects

    :returns: List of Relations
    """
    return self.objectBroker.getRelationsByID(obj.identifier)


  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def editEvent(self, eventID):
    """
    renders the base page for editing a single event

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event.groups,
                           self.getUser().identifier ==
                           event.creator.identifier)
    template = self.getTemplate('/events/event/eventModal.html')
    event = self.eventBroker.getByID(eventID)
    return EventController.__populateTemplate(event, template)

  @staticmethod
  def __populateTemplate(event, template):
    """
    Fills the the template
    """
    cbStatusValues = Status.getDefinitions()
    cbTLPValues = TLPLevel.getDefinitions()
    cbAnalysisValues = Analysis.getDefinitions()
    cbRiskValues = Risk.getDefinitions()
    string = template.render(event=event,
      cbStatusValues=cbStatusValues,
      cbAnalysisValues=cbAnalysisValues,
      cbRiskValues=cbRiskValues,
      cbTLPValues=cbTLPValues)
    return string

  # pylint: disable=R0914
  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def modifyEvent(self, **kwargs):
    """
    modifies or inserts an event with the data of the post

    :param identifier: The identifier of the event,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String
    :param status: The identifier of the statuts
    :type status: Integer
    :param tlp_index: The identifier of the TLP level
    :type tlp_index: Integer
    :param description: The desc
    :type description: String
    :param email: The email of the user
    :type email: String

    :returns: generated HTML
    """
    identifier = kwargs.get('identifier', None)
    action = kwargs.get('action', None)
    status = kwargs.get('status', None)
    tlp_index = kwargs.get('tlp_index', None)
    description = kwargs.get('description', None)
    name = kwargs.get('name', None)
    published = kwargs.get('published', None)
    first_seen = kwargs.get('first_seen', None)
    last_seen = kwargs.get('last_seen', None)
    risk = kwargs.get('risk', None)
    analysis = kwargs.get('analysis', None)
    # fill in the values
    event = Event()
    try:
      if not action == 'insert':
        template = self.getTemplate('/events/event/eventModal.html')
        event = self.eventBroker.buildEvent(identifier, action, status,
                                            tlp_index, description, name,
                                            published, first_seen, last_seen,
                                            risk, analysis, self.getUser())
        # right checks only if there is a change!!!!
        self.checkIfViewable(
                      event.groups, self.getUser().identifier ==
                      event.creator.identifier)
      if action == 'insert':
        template = self.getTemplate('/events/addEvent.html')
        self.eventBroker.insert(event)
      if action == 'update':
        self.eventBroker.update(event)
      if action == 'remove':
        self.eventBroker.removeByID(event.identifier)
      return self.returnAjaxOK()
    except ValidationException:
      self.getLogger().debug('Event is invalid')
      return EventController.__populateTemplate(event, template)
    except BrokerException as e:
      self.getLogger().error('An unexpected error occurred: {0}'.format(e))
      return 'An unexpected error occurred: {0}'.format(e)

