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

import copy
from dagr.web.controllers.base import BaseController
import cherrypy
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from datetime import datetime
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, \
                  AttributeBroker, Event, CommentBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from ce1sus.brokers.definitionbroker import ObjectDefinitionBroker, \
                  AttributeDefinitionBroker
from ce1sus.web.helpers.protection import require, requireReferer
from ce1sus.api.ticketsystem import TicketSystemBase
from dagr.db.broker import ValidationException, BrokerException
from dagr.helpers.converters import ObjectConverter

class Relation(object):
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
    cbStatusValues = Status.getDefinitions()
    cbTLPValues = TLPLevel.getDefinitions()
    cbAnalysisValues = Analysis.getDefinitions()
    cbRiskValues = Risk.getDefinitions()
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
        temp.eventID = relation.sameAttribute.object.event.identifier
        temp.identifier = temp.eventID
        temp.eventName = relation.sameAttribute.object.event.title
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
                           cbStatusValues=cbStatusValues,
                           cbTLPValues=cbTLPValues,
                           comments=event.comments,
                           cbAnalysisValues=cbAnalysisValues,
                           cbRiskValues=cbRiskValues)

  def __getRelationsObjects(self, objects):
    result = list()
    for obj in objects:
      result = result + self.__getRelationsObject(obj)
    return result

  def __getRelationsObject(self, obj):
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
    return EventController.__populateTemplate(None, event, template)

  @staticmethod
  def __populateTemplate(errorMsg, event, template):
    """
    Fills the the template
    """
    cbStatusValues = Status.getDefinitions()
    cbTLPValues = TLPLevel.getDefinitions()
    cbAnalysisValues = Analysis.getDefinitions()
    cbRiskValues = Risk.getDefinitions()
    string = template.render(errorMsg=errorMsg, event=event,
      cbStatusValues=cbStatusValues,
      cbAnalysisValues=cbAnalysisValues,
      cbRiskValues=cbRiskValues,
      cbTLPValues=cbTLPValues)
    return string

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
    params = kwargs
    identifier = params.get('identifier', None)
    action = params.get('action', None)
    status = params.get('status', None)
    tlp_index = params.get('tlp_index', None)
    description = params.get('description', None)
    name = params.get('name', None)
    published = params.get('published', None)
    first_seen = params.get('first_seen', None)
    last_seen = params.get('last_seen', None)
    risk = params.get('risk', None)
    analysis = params.get('analysis', None)
    errorMsg = None
    errors = False
    # fill in the values
    event = Event()
    if not action == 'insert':
      template = self.getTemplate('/events/event/eventModal.html')
      # dont want to change the original in case the user cancel!
      event_orig = self.eventBroker.getByID(identifier)
      event = copy.copy(event_orig)
      # right checks only if there is a change!!!!
      self.checkIfViewable(
                    event_orig.groups, self.getUser().identifier ==
                    event_orig.creator.identifier)
    if not action == 'remove':
      event.title = name
      event.description = description
      ObjectConverter.setInteger(event, 'tlp_level_id', tlp_index)
      ObjectConverter.setInteger(event, 'status_id', status)
      ObjectConverter.setInteger(event, 'published', published)
      event.modified = datetime.now()
      event.modifier = self.getUser()
      event.modifier_id = event.modifier.identifier
      if first_seen:
        ObjectConverter.setDate(event, 'first_seen', first_seen)
      else:
        event.first_seen = datetime.now()
      if last_seen:
        ObjectConverter.setDate(event, 'last_seen', last_seen)
      else:
        event.last_seen = datetime.now()
      ObjectConverter.setInteger(event, 'analysis_status_id', analysis)
      ObjectConverter.setInteger(event, 'risk_id', risk)
    try:
      if action == 'insert':
        template = self.getTemplate('/events/addEvent.html')
        event.created = datetime.now()
        event.creator = self.getUser()
        event.creator_id = event.creator.identifier
        self.eventBroker.insert(event)
      if action == 'update':
        # get original event
        self.eventBroker.update(event)
      if action == 'remove':
        self.eventBroker.removeByID(event.identifier)
    except ValidationException:
      self.getLogger().debug('Event is invalid')
      errors = True
    except BrokerException as e:
      errorMsg = 'An unexpected error occurred: {0}'.format(e)
      self.getLogger().debug('An unexpected error occurred: {0}'.format(e))
      errors = True
    if errors:
      return EventController.__populateTemplate(errorMsg, event, template)
    else:
      return self.returnAjaxOK()
