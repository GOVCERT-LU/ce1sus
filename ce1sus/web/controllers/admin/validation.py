# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Nov 13, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, privileged, requireReferer
from dagr.db.broker import BrokerException
from ce1sus.brokers.event.eventbroker import EventBroker
from dagr.web.helpers.pagination import Paginator, PaginatorOptions
from ce1sus.brokers.event.objectbroker import ObjectBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel, Analysis, Risk
from ce1sus.brokers.definition.attributedefinitionbroker import \
                  AttributeDefinitionBroker
from ce1sus.brokers.definition.objectdefinitionbroker import \
                  ObjectDefinitionBroker
from dagr.helpers.datumzait import datumzait
from ce1sus.brokers.event.attributebroker import AttributeBroker
from ce1sus.brokers.relationbroker import RelationBroker
from ce1sus.web.controllers.event.event import Relation


class ValidationController(Ce1susBaseController):

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)
    self.objectBroker = self.brokerFactory(ObjectBroker)
    self.def_attributesBroker = self.brokerFactory(AttributeDefinitionBroker)
    self.def_objectBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.attributeBroker = self.brokerFactory(AttributeBroker)
    self.relationBroker = self.brokerFactory(RelationBroker)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the user page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/validation/validationBase.html')
    self.checkIfPriviledged()
    return self.cleanHTMLCode(template.render())

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def unvalidated(self):
    template = self.mako.getTemplate('/admin/validation/recent.html')
    self.checkIfPriviledged()
    labels = [{'identifier':'#'},
              {'title':'Title'},
              {'analysis': 'Analysis'},
              {'risk':'Risk'},
              {'status': 'Status'},
              {'tlp':'TLP'},
              {'modified':'Last modification'},
              {'last_seen':'Last seen'},
              {'creatorGroup.name': 'Created By'}]
    # get only the last 200 events to keep the page small

    lists = self.eventBroker.getAllUnvalidated(200, 0)
    paginatorOptions = PaginatorOptions('/admin/validation/unvalidated',
                                        'validationTabsTabContent')
    paginatorOptions.addOption('NEWTAB',
                               'VIEW',
                               '/admin/validation/event/',
                               contentid='',
                               autoReload=False,
                               tabTitle='Event')
    paginator = Paginator(items=lists,
                          labelsAndProperty=labels,
                          paginatorOptions=paginatorOptions)
    paginator.itemsPerPage = 100
    return self.cleanHTMLCode(template.render(paginator=paginator))




  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def event(self, eventID):
    """
    renders the base page for displaying events

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfPriviledged()
    template = self.mako.getTemplate('/admin/validation/eventValBase.html')
    return self.cleanHTMLCode(template.render(eventID=eventID))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def eventDetails(self, eventID):
    """
    renders the event page for displaying a single event

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/admin/validation/eventDetails.html')
    event = self.eventBroker.getByID(eventID)
    # right checks
    self.checkIfPriviledged()
    paginatorOptions = PaginatorOptions('/events/recent',
                                        'eventsTabTabContent')
    paginatorOptions.addOption('TAB',
                          'VIEW',
                          '/admin/validation/eventObjects/{0}'.format(eventID),
                          contentid='',
                          tabid='eventObjects{0}'.format(eventID))



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
                               autoReload=False,
                               tabTitle='Event')

    relationPaginator = Paginator(items=list(),
                          labelsAndProperty=relationLabels,
                          paginatorOptions=relationsPaginatorOptions)
    relationPaginator.itemsPerPage = 3

    try:
      # get for each object
      # prepare list
      #
      for event_rel in self.relationBroker.getRelationsByEvent(event):
        temp = Relation()
        rel_event = event_rel.rel_event
        try:
          if rel_event.identifier != event.identifier:
            self.checkIfViewable(rel_event)
          temp.eventID = rel_event.identifier
          temp.identifier = rel_event.identifier
          temp.eventName = rel_event.title
          temp.eventFirstSeen = rel_event.first_seen
          temp.eventLastSeen = rel_event.last_seen
          if not temp in relationPaginator.list:
            relationPaginator.list.append(temp)
        except cherrypy.HTTPError:
          self.getLogger().debug(('User {0} is not '
                                    + 'authorized').format(self.getUser(True)))

    except BrokerException as e:
      self.getLogger().error(e)

    return self.cleanHTMLCode(template.render(objectList=event.objects,
                           relationPaginator=relationPaginator,
                           event=event,
                           comments=event.comments,
                           cbStatusValues=Status.getDefinitions(),
                           cbTLPValues=TLPLevel.getDefinitions(),
                           cbAnalysisValues=Analysis.getDefinitions(),
                           cbRiskValues=Risk.getDefinitions()))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def eventObjects(self, eventID, objectID=None):
    """
     renders the file with the base layout of the main object page

    :param objectID: the identifier of the object (only set if the details
                     should be displayed of this object)
    :type objectID: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/validation/eventValobjects.html')
    event = self.eventBroker.getByID(eventID)
    self.checkIfPriviledged()

    # if event has objects

    labels = [{'identifier':'#'},
              {'key':'Type'},
              {'value':'Value'},
              {'isIOC': 'Is an IOC'}]
    # mako will append the missing url part
    paginatorOptions = PaginatorOptions(('/events/event/objects/'
                                         + 'objects/{0}/%(objectID)s/').format(
                                                                      eventID),
                                      'eventTabs{0}TabContent'.format(eventID))
    # mako will append the missing url part
    paginatorOptions.addOption('MODAL',
                               'VIEW',
                               ('/admin/validation/'
                                + 'viewAttributeDetails/{0}/%(objectID)s/').format(eventID),
                               modalTitle='View Attribute')
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

    objects = event.objects
    if objectID is None:
      try:
        objectID = getattr(cherrypy, 'session')['instertedObject']
        getattr(cherrypy, 'session')['instertedObject'] = None
      except KeyError:
        objectID = None

    return self.cleanHTMLCode(template.render(eventID=eventID,
                        objectList=objects,
                        cbObjDefinitions=self.def_objectBroker.getCBValues(),
                        cbAttributeDefintiionsDict=cbAttributeDefintiionsDict,
                        paginator=paginator,
                        objectID=objectID))

  def __validateObjects(self, objects):
    for obj in objects:
      obj.bitValue.isValidated = True
      # perfom validation of object attribtues
      for attribtue in obj.attributes:
        attribtue.bitValue.isValidated = True
      self.__validateObjects(obj.children)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def validateEvent(self, eventID):
    self.checkIfPriviledged()
    try:
      event = self.eventBroker.getByID(eventID)
      # perfom validation of event
      event.bitValue.isValidated = True
      # update modifier
      event.modifier = self.getUser()
      event.modifier_id = event.modifier.identifier
      event.modified = datumzait.utcnow()
      event.published = 1
      # check if the event has a group
      if event.creatorGroup is None:
        # if not add the default group of the validating user
        event.creatorGroup = self.getUser().defaultGroup

      # perform validation of objects
      self.__validateObjects(event.objects)
      self.eventBroker.update(event)
      return self.returnAjaxOK()
    except BrokerException as e:
      return '{0}'.format(e)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def viewAttributeDetails(self, eventID, objectID, attributeID):
    """
     renders the file with the requested attribute
    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfPriviledged()
    template = self.getTemplate('/events/event/attributes/attributesModal.html'
                                )
    obj = self.objectBroker.getByID(objectID)
    cbDefinitions = self.def_attributesBroker.getCBValues(
                                                    obj.definition.identifier)
    attribute = self.attributeBroker.getByID(attributeID)
    return self.cleanHTMLCode(template.render(eventID=eventID,
                           objectID=objectID,
                           attribute=attribute,
                           cbDefinitions=cbDefinitions,
                           errorMsg=None,
                           enabled=False))
