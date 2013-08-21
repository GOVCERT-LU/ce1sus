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
class GroupsController(BaseController):
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
  def groups(self, eventID):
    """
    Event page listing
    """
    template = self.mako.getTemplate('/events/event/groups/groups.html')
    event = self.eventBroker.getByID(eventID)

    # right checks
    self.checkIfViewable(event.groups,
                         self.getUser().identifier == event.creator.identifier)


    remainingGroups = self.eventBroker.getGroupsByEvent(event.identifier, False)
    return template.render(eventID=event.identifier,
                           remainingGroups=remainingGroups,
                           eventGroups=event.groups)

  @cherrypy.expose
  @require()
  def modifyGroups(self, eventID, operation, remainingGroups=None,
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
    try:
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
            self.eventBroker.removeGroupFromEvent(eventID, eventGroups)
          else:
            for groupID in eventGroups:
              self.eventBroker.removeGroupFromEvent(eventID, groupID, False)
            self.eventBroker.session.commit()
      return self.returnAjaxOK()
    except BrokerException as e:
      return e
