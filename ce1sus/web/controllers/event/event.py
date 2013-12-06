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

import cherrypy

from ce1sus.brokers.definition.attributedefinitionbroker import \
  AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
  ObjectDefinitionBroker
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.event.commentbroker import CommentBroker
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from ce1sus.web.controllers.base import Ce1susBaseController
from ce1sus.web.helpers.protection import require, requireReferer
from dagr.db.broker import ValidationException, BrokerException
from dagr.web.helpers.pagination import Paginator, PaginatorOptions


# pylint: disable=R0903,R0902
class Relation(object):
  """
  Relation container used for displaying the relations
  """
  def __init__(self):
    self.identifier = 0
    self.eventID = 0
    self.eventFirstSeen = None
    self.eventLastSeen = None
    self.eventName = 0
    self.objectID = 0
    self.objectName = 0
    self.attributeID = 0
    self.attributeName = 0
    self.attributeValue = 0


# pylint: disable=R0903,R0902
class Object4Paginator(object):
  """
  Container only used for displaying the objects in the event view
  """
  def __init__(self):
    self.identifier = 0
    self.type = 0
    self.isChildOf = 0


class EventController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
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
    self.checkIfViewable(event)
    template = self.mako.getTemplate('/events/event/eventBase.html')
    return self.cleanHTMLCode(template.render(eventID=eventID,
                           owner=self.isEventOwner(event)))

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
    self.checkIfViewable(event)
    paginatorOptions = PaginatorOptions('/events/recent',
                                        'eventsTabTabContent')
    paginatorOptions.addOption('TAB',
                          'VIEW',
                          '/events/event/objects/objects/{0}'.format(eventID),
                          contentid='',
                          tabid='eventObjects{0}'.format(eventID))

    objectPaginator = Paginator(items=list(),
                          labelsAndProperty=[{'identifier':'#'},
                                              {'type':'Type'},
                                              {'isChildOf':'Child Of'}],
                          paginatorOptions=paginatorOptions)
    objectPaginator.itemsPerPage = 3

    if self.isEventOwner(event):
      objectList = (self.objectBroker.getObjectsOfEvent(eventID)
                + self.objectBroker.getChildObjectsForEvent(eventID))
    else:
      objectList = (self.objectBroker.getViewableOfEvent(eventID)
                + self.objectBroker.getViewableChildObjectsForEvent(eventID))


    for item in objectList:
      newItem = Object4Paginator()
      newItem.identifier = item.identifier
      newItem.type = item.definition.name
      if item.parentObject_id is None:
        newItem.isChildOf = ''
      else:
        newItem.isChildOf = '#{0}'.format(item.parentObject_id)
      objectPaginator.list .append(newItem)

    relationLabels = [{'eventID':'Event #'},
                      {'eventName':'Event Name'},
                      {'eventFirstSeen':'First Seen'},
                      {'eventLastSeen':'Last Seen'}]

    relationsPaginatorOptions = PaginatorOptions('/events/recent',
                                                 'eventsTabTabContent')
    relationsPaginatorOptions.addOption('NEWTAB',
                               'VIEW',
                               '/events/event/view/',
                               contentid='',
                               autoReload=True)

    relationPaginator = Paginator(items=list(),
                          labelsAndProperty=relationLabels,
                          paginatorOptions=relationsPaginatorOptions)
    relationPaginator.itemsPerPage = 3

    try:
      # get for each object
      # prepare list
      #
      for event_rel in self.eventBroker.getRelatedEvents(event):
        temp = Relation()
        try:
          if event_rel.identifier != event.identifier:
            self.checkIfViewable(event_rel)
          temp.eventID = event_rel.identifier
          temp.identifier = event_rel.identifier
          temp.eventName = event_rel.title
          temp.eventFirstSeen = event_rel.first_seen
          temp.eventLastSeen = event_rel.last_seen
          if not temp in relationPaginator.list:
            relationPaginator.list.append(temp)
        except cherrypy.HTTPError:
          self.getLogger().debug(('User {0} is not '
                                    + 'authorized').format(self.getUser(True)))

    except BrokerException as e:
      self.getLogger().error(e)

    return self.cleanHTMLCode(template.render(objectPaginator=objectPaginator,
                           relationPaginator=relationPaginator,
                           event=event,
                           comments=event.comments))

  def __getRelationsObjects(self, objects):
    """
    Returns the relation of the given objects

    :param objects: list of Objects
    :type objects: List of Objects

    :returns: List of Relations
    """
    objectIDList = list()
    for obj in objects:
      objectIDList.append(obj.identifier)
    relations = self.objectBroker.getRelationsByObjectIDList(objectIDList)

    return relations

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def editEvent(self, eventID):
    """
    renders the base page for editing a single event

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event)
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
    string = self.cleanHTMLCode(template.render(event=event,
      cbStatusValues=cbStatusValues,
      cbAnalysisValues=cbAnalysisValues,
      cbRiskValues=cbRiskValues,
      cbTLPValues=cbTLPValues))
    return string

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def details(self, eventID):
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event)
    template = self.mako.getTemplate('/events/event/details.html')
    return self.cleanHTMLCode(template.render(event=event,
                           cbStatusValues=Status.getDefinitions(),
                           cbTLPValues=TLPLevel.getDefinitions(),
                           cbAnalysisValues=Analysis.getDefinitions(),
                           cbRiskValues=Risk.getDefinitions(),
                           owner=self.isEventOwner(event)))

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def editDetails(self, eventID):
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event)

    template = self.mako.getTemplate('/events/event/editDetails.html')
    return self.cleanHTMLCode(template.render(event=event,
                           cbStatusValues=Status.getDefinitions(),
                           cbTLPValues=TLPLevel.getDefinitions(),
                           cbAnalysisValues=Analysis.getDefinitions(),
                           cbRiskValues=Risk.getDefinitions()))

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
    event = self.eventBroker.buildEvent(identifier,
                                        action,
                                        status,
                                        tlp_index,
                                        description,
                                        name,
                                        published,
                                        first_seen,
                                        last_seen,
                                        risk,
                                        analysis,
                                        self.getUser())

    try:
      if not action == 'insert':
        template = self.getTemplate('/events/event/editDetails.html')

        # right checks only if there is a change!!!!
        self.checkIfViewable(event)
      if action == 'insert':
        template = self.getTemplate('/events/addEvent.html')
        event.bitValue.isWebInsert = True
        event.bitValue.isValidated = True
        self.eventBroker.insert(event)
      if action == 'update':
        self.eventBroker.update(event)
      if action == 'remove':
        self.eventBroker.removeByID(event.identifier)
      return self.returnAjaxOK()
    except ValidationException:

      self.getLogger().debug('Event is invalid')
      return (self.returnAjaxPostError()
                        + EventController.__populateTemplate(event, template))

    except BrokerException as e:
      self.getLogger().error('An unexpected error occurred: {0}'.format(e))
      return 'An unexpected error occurred: {0}'.format(e)

  @require(requireReferer(('/internal')))
  @cherrypy.expose
  def relations(self, eventID):
    template = self.mako.getTemplate('/events/event/relations.html')

    event = self.eventBroker.getByID(eventID)
    # right checks
    if self.isAdminArea():
      self.checkIfPriviledged()
    else:
      self.checkIfViewable(event)

    relationLabels = [{'eventID':'Event #'},
                      {'eventName':'Event Name'},
              {'objectID':'Object #'},
              {'objectName':'Object Name'},
              {'attributeID':'Attribute #'},
              {'attributeName':'Attribute Name'},
              {'attributeValue':'Attribute Value'}]

    relationsPaginatorOptions = PaginatorOptions('/events/recent',
                                                 'eventsTabTabContent')
    relationsPaginatorOptions.addOption('NEWTAB',
                               'VIEW',
                               '/events/event/view/',
                               contentid='')

    relationPaginator = Paginator(items=list(),
                          labelsAndProperty=relationLabels,
                          paginatorOptions=relationsPaginatorOptions)

    try:
      # get for each object
      # prepare list
      #
      for relation in self.__getRelationsObjects(event.objects):
        temp = Relation()
        # TODO Check if the event is viewable for the user
        if relation.sameAttribute.object.event is None:
          event_rel = relation.sameAttribute.object.parentObject.event
        else:
          event_rel = relation.sameAttribute.object.event
          try:
            if event_rel.identifier != event.identifier:
              self.checkIfViewable(event_rel)
            temp.eventID = event_rel.identifier
            temp.identifier = event_rel.identifier
            temp.eventName = event_rel.title
            temp.objectID = relation.sameAttribute.object.identifier
            temp.objectName = relation.sameAttribute.object.definition.name
            temp.attributeID = relation.sameAttribute.identifier
            temp.attributeName = relation.sameAttribute.definition.name
            temp.attributeValue = relation.sameAttribute.value
            relationPaginator.list.append(temp)
          except cherrypy.HTTPError:
            self.getLogger().debug(('User {0} is not '
                                    + 'authorized').format(self.getUser(True)))

    except BrokerException as e:
      self.getLogger().error(e)
    return self.cleanHTMLCode(template.render(relationPaginator=relationPaginator))
