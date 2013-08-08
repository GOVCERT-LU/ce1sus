"""module holding all controllers needed for the event handling"""

import copy
from ce1sus.web.controllers.base import BaseController
import cherrypy
from ce1sus.web.helpers.pagination import Paginator
from datetime import datetime
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, \
                  AttributeBroker, Event, Object, Attribute, Comment, \
                  CommentBroker, Ticket, TicketBroker
from ce1sus.brokers.staticbroker import Status, TLPLevel
from ce1sus.brokers.definitionbroker import ObjectDefinitionBroker, \
                  AttributeDefinitionBroker, AttributeDefinition
from ce1sus.web.helpers.protection import require
from cherrypy._cperror import HTTPRedirect
import ce1sus.helpers.string as string
from ce1sus.helpers.rt import RTHelper
import types
from ce1sus.db.broker import NothingFoundException, ValidationException, BrokerException
import ce1sus.helpers.converters as convert

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
    self.ticketBroker = self.brokerFactory(TicketBroker)

  @cherrypy.expose
  @require()
  def index(self):
    """
    index page

    :returns: generated HTML
    """
    return self.events()

  def updateEvent(self, event, updateLastSeen=True):
    """
      Updates the last seen value

      :param event: the event to be updated
      :type event: Event
    """
    if updateLastSeen:
      event.last_seen = datetime.now()
    event.modified = datetime.now()
    try:
      self.eventBroker.update(event)
    except Exception as e:
      self.getLogger().info(e)



  @cherrypy.expose
  @require()
  def events(self):
    """
    Renders the event Page (list of all events)

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/events.html')

    labels = [{'identifier':'#'},
              {'label':'Title'},
              {'modified':'Last modification'},
              {'last_seen':'Last seen'},
              {'status': 'Status'},
              {'tlp':'TLP'}]

    # get only the last 200 events to keep the page small
    user = self.getUser()
    lists = self.eventBroker.getAllForUser(user, 200, 0)




    paginator = Paginator(items=lists,
                          labelsAndProperty=labels,
                          baseUrl='/events/events',
                          showOptions=False)
    paginator.showView = True

    return template.render(paginator=paginator)


  @cherrypy.expose
  @require()
  def event(self, identifier, failedEvent=None,
            commentObj=None, action=None, errorMsg=None):
    """"
    Renders the page for a single event

    :param identifier: the identifier for the event to display
    :type identifier: Integer

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/view.html')
    event = self.eventBroker.getByID(identifier)

    # right checks
    self.checkIfViewable(event.groups, self.getUser().identifier == event.creator.identifier)

    cbPublishedValues = {'No':0, 'Yes':1}
    cbStatusValues = Status.getDefinitions()
    cbTLPValues = TLPLevel.getDefinitions()

    objectLabels = [{'identifier':'#'},
              {'definition.name':'Type'},
              {'creator.username':'Created by'},
              {'created':'CreatedOn'}]


    objectPaginator = Paginator(items=event.objects,
                          labelsAndProperty=objectLabels,
                          baseUrl='/events/eventObject',
                          showOptions=False)

    objectPaginator.showView = True

    objectPaginator.itemsPerPage = 3

    ticketLabels = [{'identifier':'#'},
              {'link':'Ticket Number'},
              {'creator.username':'Created by'},
              {'created':'CreatedOn'}]

    tickets = list()
    # some foo so that the paginator works
    for ticket in event.tickets:
      url = '<a href="{1}Ticket/Display.html?id={0}" target="_blank">{0}</a>'.format(ticket.ticket, self.config.get('rturl'))
      setattr(ticket, 'link', url)
      tickets.append(ticket)

    ticketPaginator = Paginator(items=tickets,
                          labelsAndProperty=ticketLabels,
                          baseUrl='/events/eventTickets',
                          showOptions=False)
    ticketPaginator.showDelete = True

    ticketPaginator.itemsPerPage = 3

    eventLabels = [{'identifier':'#'},
              {'label':'Name'},
              {'created':'CreatedOn'}]

    eventPaginator = Paginator(items=list(),
                          labelsAndProperty=eventLabels,
                          baseUrl='/events/events',
                          showOptions=True)
    eventPaginator.itemsPerPage = 3

    if failedEvent is None:
      editEvent = event
      errors = False
    else:
      editEvent = failedEvent
      errors = True

    # gather all comments for this event
    try:
      comments = self.commentBroker.getAllByEventID(identifier)
    except NothingFoundException:
      comments = None

    if commentObj is None:
      commentErrors = False
    else:
      if action == 'viewedit':
        action = None
        commentErrors = True
      else:
        commentErrors = not commentObj.validate()

    return template.render(objectPaginator=objectPaginator,
                           eventPaginator=eventPaginator,
                           ticketPaginator=ticketPaginator,
                           event=event,
                           editEvent=editEvent,
                           cbPublishedValues=cbPublishedValues,
                           cbStatusValues=cbStatusValues,
                           cbTLPValues=cbTLPValues,
                           errors=errors,
                           commentObj=commentObj,
                           comments=comments,
                           commentErrors=commentErrors)

  @require()
  @cherrypy.expose
  def addEvent(self, event=None):
    """
    Renders the page for adding an event

    :param event: Is not null in case of an erroneous input
    :type event: Event

    :returns: generated HTML
    """
    template = self.mako.getTemplate('/events/addEvent.html')
    cbPublishedValues = {'No':0, 'Yes':1}
    cbStatusValues = Status.getDefinitions()
    cbTLPValues = TLPLevel.getDefinitions()

    return template.render(event=event, cbPublishedValues=cbPublishedValues,
                           cbStatusValues=cbStatusValues,
                           cbTLPValues=cbTLPValues, today=datetime.now())


  @require()
  @cherrypy.expose
  def modifyEvent(self, identifier=None, action=None, status=None,
                  tlp_index=None, description=None,
                  name=None, published=None,
                  first_seen=None, last_seen=None):
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

    errors = False
    errorMsg = None

    # fill in the values
    event = Event()
    if not action == 'insert':
      event_orig = self.eventBroker.getByID(identifier)
      # dont want to change the original in case the user cancel!
      event = copy.copy(event_orig)

      # right checks only if there is a change!!!!
      self.checkIfViewable(
                    event.groups, self.getUser().identifier ==
                    event.creator.identifier)
    if not action == 'remove':
      event.title = name
      event.description = description
      convert.setInteger(event, 'tlp_level_id', tlp_index)
      convert.setInteger(event, 'status_id', status)
      convert.setInteger(event, 'published', published)
      event.modified = datetime.now()
      convert.setDate(event, 'first_seen', first_seen)
      convert.setDate(event, 'last_seen', last_seen)



    if action == 'insert':
      event.created = datetime.now()
      event.creator = self.getUser()
      event.user_id = event.creator.identifier
      try:
        self.eventBroker.insert(event)
        identifier = event.identifier
        event = None
        action = None
      except ValidationException:
        self.getLogger().debug('Event is invalid')
        errors = True
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None
        event = None

    if action == 'update':
      # get original event
      try:
        self.eventBroker.update(event)
        event = None
        action = None
      except ValidationException:
        self.getLogger().debug('Event is invalid')
        errors = True
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None
        event = None

    if action == 'remove':
      try:
        self.eventBroker.removeByID(event.identifier)
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
      action = None
      event = None

    if errors and action == 'insert':
      return self.addEvent(event)


    if action == 'remove':
      return self.events()
    else:
      return self.event(identifier=identifier,
                        failedEvent=event,
                        action=action,
                        errorMsg=errorMsg)



  @cherrypy.expose
  @require()
  def eventObjects(self, identifier, objIdentifier=None, action=None,
                   attribute=None, attributeEnable=False,
                   showAttribute=False, failedAttr=None):
    """
    List all objects of a given event
    """
    template = self.mako.getTemplate('/events/objects.html')
    event = self.eventBroker.getByID(identifier)

    # right checks
    self.checkIfViewable(event.groups, self.getUser().identifier ==
                         event.creator.identifier)



    objectList = list()
    if objIdentifier is None:
      if (len(event.objects) > 0):
        objectList = event.objects
      else:
        objectList.append(None)
    else:
      obj = self.objectBroker.getByID(objIdentifier)
      objectList.append(obj)


    labels = [{'identifier':'#'},
              {'key':'Type'},
              {'value':'Value'},
              {'creator.username':'Creator'},
              {'created':'CreatedOn'}]

    # will be associated in the view!!! only to keep it simple!
    paginator = Paginator(items=list(),
                          labelsAndProperty=labels,
                          baseUrl='/events/eventAttribute',
                          showOptions=True)

    cbObjDefinitions = self.def_objectBroker.getCBValues()


    cbAttributeDefintiionsDict = dict()
    # fill dictionary of attribute definitions but only the needed ones
    for obj in objectList:
      if not obj is None:
        if not obj.definition.identifier in cbAttributeDefintiionsDict:
          attributes = self.def_attributesBroker.getCBValues(
                                                      obj.definition.identifier)
          cbAttributeDefintiionsDict[obj.definition.identifier] = attributes


    return template.render(event=event,
                        objectList=objectList,
                        paginator=paginator,
                        cbObjDefinitions=cbObjDefinitions,
                        attribute=attribute,
                        attributeEnable=attributeEnable,
                        cbAttributeDefintiionsDict=cbAttributeDefintiionsDict,
                        showAttribute=showAttribute,
                        failedAttr=failedAttr,
                        action=action)

  @cherrypy.expose
  @require()
  def insertEventObject(self, identifier=None, definition=None):
    """
    Inserts an an event object.

    :param identifier: The identifier of the event
    :type identifier: Integer
    :param definition: The identifier of the definition associated to the object
    :type definition: Integer

    :returns: generated HTML
    """

    event = self.eventBroker.getByID(identifier)

    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)

    # Here is an insertion only so the action parameter is not needed, btw.
    # the object has no real editable values since if the definition would
    # change also the attributes have to change as some might be incompatible!!

    obj = Object()
    obj.identifier = None
    obj.def_object_id = definition
    obj.created = datetime.now()
    obj.event_id = identifier
    obj.event = event
    obj.user_id = self.getUser().identifier
    try:
      self.eventBroker.insert(obj)
      self.updateEvent(event)
      obj = None
    except ValidationException:
      self.getLogger().debug('Event is invalid')
    except BrokerException as e:
      self.getLogger().critical(e)
      obj = None

    return self.eventObjects(identifier, objIdentifier=obj.identifier)

  @cherrypy.expose
  @require()
  def removeObject(self, identifier=None, objIdentifier=None):
    """
    Removes an object
    """
    event = self.eventBroker.getByID(identifier)

    # right checks
    self.checkIfViewable(event.groups, self.getUser().identifier ==
                         event.creator.identifier)

    # remove object
    try:
      self.objectBroker.removeByID(objIdentifier)
    except BrokerException as e:
      self.getLogger().critical(e)
    return self.eventObjects(identifier=identifier)



  @cherrypy.expose
  @require()
  def eventTickets(self, identifier):
    """
    Lists all event tickets and tickets
    """
    template = self.mako.getTemplate('/events/tickets.html')
    event = self.eventBroker.getByID(identifier)

    # right checks
    self.checkIfViewable(event.groups, self.getUser().identifier ==
                         event.creator.identifier)

    labels = [{'identifierLink':'#'},
              {'title':'Title'},
              {'selector':'Options'}]


    paginator = Paginator(items=RTHelper.getInstance().getAllTickets(),
                          labelsAndProperty=labels,
                          baseUrl='/events/tickets',
                          showOptions=False)

    ticketLabels = [{'identifier':'#'},
              {'link':'Ticket Number'},
              {'creator.username':'Created by'},
              {'created':'CreatedOn'}]

    tickets = list()
    # some foo so that the paginator works
    for ticket in event.tickets:
      url = ('<a href="{1}/Ticket/Display.html?id={0}" ' +
             'target="_blank">{0}</a>'.format(
                        ticket.ticket, self.config.get('rturl')))
      setattr(ticket, 'link', url)
      tickets.append(ticket)

    ticketPaginator = Paginator(items=tickets,
                          labelsAndProperty=ticketLabels,
                          baseUrl='/events/eventTickets',
                          showOptions=False)
    ticketPaginator.showDelete = True


    # update last_seen
    self.updateEvent(event)

    return template.render(event=event,
                           paginator=paginator,
                           ticketPaginator=ticketPaginator)
  @cherrypy.expose
  @require()
  def modifyEventTicket(self,
                        eventID,
                        action,
                        identifier=None,
                        ticketTable_length=None,
                        tickets=None):
    """
    Processes the modifications of an event
    """
    event = self.eventBroker.getByID(eventID)

    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)
    if action == 'insert':
      # create and insert tickets
      try:
        if not tickets is None:
          if isinstance(tickets, types.StringTypes):
            ticket = Ticket()
            ticket.identifier = None
            ticket.created = datetime.now()
            ticket.ticket = tickets
            ticket.creator = self.getUser()
            ticket.user_id = ticket.creator.identifier
            ticket.events.append(event)
            self.ticketBroker.insert(ticket)
          else:
            for ticketID in tickets:
              # fillup tickets
              ticket = Ticket()
              ticket.identifier = None
              ticket.created = datetime.now()
              ticket.ticket = ticketID
              ticket.creator = self.getUser()
              ticket.user_id = ticket.creator.identifier
              ticket.events.append(event)
              self.ticketBroker.insert(ticket, False)
            # commit when all are set up
            self.ticketBroker.session.commit()
      except BrokerException as e:
        self.getLogger().critical(e)
    return self.eventTickets(identifier=event.identifier)


  @cherrypy.expose
  @require()
  def eventTicketsPaginator(self, action, identifier):
    """
    Pagination for the tickets
    """
    eventID = None
    if action == 'remove':
      ticket = self.ticketBroker.getByID(identifier)

      if (len(ticket.events) > 0):
        eventID = ticket.events[0].identifier
      try:
        self.ticketBroker.removeByID(identifier)
      except BrokerException as e:
        self.getLogger().critical(e)

    if eventID is None:
      return self.events()
    else:
      return self.eventTickets(identifier=eventID)



  @cherrypy.expose
  @require()
  def eventGroups(self, identifier):
    """
    Event page listing
    """
    template = self.mako.getTemplate('/events/groups.html')
    event = self.eventBroker.getByID(identifier)

    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)


    remainingGroups = self.eventBroker.getGroupsByEvent(event.identifier, False)
    return template.render(eventID=event.identifier,
                           remainingGroups=remainingGroups,
                           eventGroups=event.groups)

  @cherrypy.expose
  @require()
  def editEventGroups(self, eventID, operation, remainingGroups=None,
                     eventGroups=None):
    """
    modifies the relation between a user and his groups

    :param eventID: The eventID of the event
    :type eventID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingGroups: The identifiers of the groups which the event is not
                            attributed to
    :type remainingGroups: Integer array
    :param eventGroups: The identifiers of the groups which the event is
                       attributed to
    :type eventGroups: Integer array

    :returns: generated HTML
    """

    if operation == 'add':
      if not (remainingGroups is None):
        if isinstance(remainingGroups, types.StringTypes):
          self.eventBroker.addGroupToEvent(eventID, remainingGroups)
        else:
          for groupID in remainingGroups:
            self.eventBroker.addGroupToEvent(eventID, groupID, False)
          self.eventBroker.session.commit()
    else:
      if not (eventGroups is None):
        if isinstance(eventGroups, types.StringTypes):
          self.eventBroker.removeGroupFromEvent(eventID, remainingGroups)
        else:
          for groupID in eventGroups:
            self.eventBroker.removeGroupFromEvent(eventID, groupID, False)
          self.eventBroker.session.commit()
    return self.eventGroups(identifier=eventID)

  @cherrypy.expose
  @require()
  def eventsPaginator(self, action, identifier):
    """
    Decider called by the paginator to redirect to the right page.

    Note: This paginator is embedded in the events page.

    :param action: The action selected in the paginator (view, edit, delete)
    :type action: String
    :param identifier: Identifier of the selected line
    :type identifier: Integer

    :returns: generated HTML
    """

    if action == 'view':
      return self.event(identifier)
    else:
      return self.modifyEvent(identifier, action)

  @cherrypy.expose
  @require()
  def eventObjectPaginator(self, action, identifier):
    """
    Decider called by the paginator to redirect to the right page

    Note: This paginator is embedded in the view (view event) page.

    :param action: The action selected in the paginator (view, edit, delete)
    :type action: String
    :param identifier: Identifier of the selected line
    :type identifier: Integer

    :returns: generated HTML
    """
    if action == 'view':
      obj = self.objectBroker.getByID(identifier)
      event_id = obj.event.identifier
      return self.eventObjects(identifier=event_id,
                               objIdentifier=obj.identifier,
                               action=action)

  @cherrypy.expose
  @require()
  def modifyObjectAttribute(self, identifier=None, attrIdentifier=None,
                            objIdentifier=None, definition=None, value=None,
                            action=None):
    """
    Modification on the attributes of objects
    """
    event = self.eventBroker.getByID(identifier)

    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)

    obj = self.objectBroker.getByID(objIdentifier)

    attribute = Attribute()
    attribute.object_id = obj.identifier
    attribute.object = obj

    attribute.def_attribute_id = definition
    attribute.definition = AttributeDefinition()

    attribute.value = value
    attribute.user_id = self.getUser().identifier
    attribute.creator = self.getUser()


    definitionObj = self.def_attributesBroker.getByID(definition)
    attribute.definition = definitionObj
    attribute.def_attribute_id = attribute.definition.identifier

    errors = False
    try:
      if action == 'insert':
        self.attributeBroker.insert(attribute)
      if action == 'update':
        attribute.identifier = attrIdentifier
        temp = self.attributeBroker.getByID(attrIdentifier)
        attribute.value_id = temp.value_id
        self.attributeBroker.update(attribute)
      action = None

      # update last_seen
      self.updateEvent(event, False)
    except ValidationException as e:
      errors = True
      self.getLogger().info(e)



    return self.eventObjects(identifier=identifier, objIdentifier=objIdentifier,
                             action=action, attribute=attribute,
                             attributeEnable=errors, showAttribute=errors,
                             failedAttr=attribute)


  @cherrypy.expose
  @require()
  def eventAttributePaginator(self, action, identifier):
    """
    Decider called by the paginator to redirect to the right page

    Note: This paginator is embedded in the object details page.

    :param action: The action selected in the paginator (view, edit, delete)
    :type action: String
    :param identifier: Identifier of the selected line
    :type identifier: Integer

    :returns: generated HTML
    """
    attribute = self.attributeBroker.getByID(identifier)
    obj = attribute.object
    event_id = obj.event.identifier

    if action == 'view':
      return self.eventObjects(identifier=event_id,
                               objIdentifier=obj.identifier, action=action,
                               attribute=attribute, attributeEnable=False,
                               showAttribute=True)
    if action == 'edit':
      return self.eventObjects(identifier=event_id,
                               objIdentifier=obj.identifier, action='update',
                               attribute=attribute, attributeEnable=True,
                               showAttribute=True)
    if action == 'remove':
      self.attributeBroker.removeByID(attribute.identifier)

      return self.eventObjects(identifier=event_id,
                               objIdentifier=obj.identifier, action=action,
                               attribute=attribute, attributeEnable=False,
                               showAttribute=False)

  @cherrypy.expose
  @require()
  def modifyEventCommnet(self, identifier=None, commentIdentifier=None,
                         commentText=None, action=None):
    """
    Modifications of a comment
    """
    event = self.eventBroker.getByID(identifier)
    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)

    comment = Comment()
    errorMsg = ''
    if not action == 'insert':
      comment_orig = self.commentBroker.getByID(commentIdentifier)
      # dont want to change the original in case the user cancel!
      comment = copy.copy(comment_orig)

    if action == 'insert':
      comment.comment = commentText
      comment.creator = self.getUser()
      comment.user_id = comment.creator.identifier
      comment.event = event
      comment.event_id = event.identifier
      comment.created = datetime.now()

      try:
        self.commentBroker.insert(comment)
        identifier = event.identifier
        comment = None
        action = None
      except ValidationException:
        self.getLogger().debug('Event is invalid')
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None


    if action == 'edit':
      comment.comment = commentText

      try:
        self.commentBroker.update(comment)
        identifier = event.identifier
        comment = None
        action = None
      except ValidationException:
        self.getLogger().debug('Event is invalid')
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None

    if action == 'remove':
      try:
        self.commentBroker.removeByID(comment.identifier)
        identifier = event.identifier
        comment = None
        action = None
      except ValidationException:
        self.getLogger().debug('Event is invalid')
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None


    return self.event(identifier, commentObj=comment, action=action,
                      errorMsg=errorMsg)



  @cherrypy.expose
  @require()
  def logout(self):
    self.clearSession()
    raise HTTPRedirect('/index')
