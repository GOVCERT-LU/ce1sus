# -*- coding: utf-8 -*-

"""
module handing the group pages

Created: Aug 21, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, requireReferer
import types
from dagr.db.broker import BrokerException
from ce1sus.brokers.event.eventbroker import EventBroker


class GroupsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.eventBroker = self.brokerFactory(EventBroker)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def groups(self, eventID):
    """
    Event page listing
    """
    template = self.mako.getTemplate('/events/event/groups/groups.html')
    event = self.eventBroker.getByID(eventID)
    # right checks
    if self.isAdminArea():
      self.checkIfPriviledged()
    else:
      self.checkIfViewable(event)
    remainingGroups = self.eventBroker.getGroupsByEvent(event.identifier,
                                                        False)
    remainingSubGroups = self.eventBroker.getSubGroupsByEvent(event.identifier,
                                                           False)

    return self.cleanHTMLCode(template.render(eventID=event.identifier,
                           remainingGroups=remainingGroups,
                           eventGroups=event.groups,
                           remainingSubGroups=remainingSubGroups,
                           eventSubGroups=event.maingroups,
                           owner=self.isEventOwner(event)))

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def modifyGroups(self, eventID, operation, remainingGroups=None,
                     eventGroups=None):
    """
    modifies the relation between a user and his groups

    :param eventID: The eventID of the event
    :type eventID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingGroups: The identifiers of the groups which the event is
                            not attributed to
    :type remainingGroups: Integer array
    :param eventGroups: The identifiers of the groups which the event is
                       attributed to
    :type eventGroups: Integer array

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    if self.isAdminArea():
      self.checkIfPriviledged()
    else:
      self.checkIfViewable(event)


    try:
      if operation == 'add':
        if not (remainingGroups is None):
          if isinstance(remainingGroups, types.StringTypes):
            self.eventBroker.addGroupToEvent(eventID, remainingGroups)
          else:
            for groupID in remainingGroups:
              self.eventBroker.addGroupToEvent(eventID, groupID, False)
            self.eventBroker.doCommit(True)
      else:
        if not (eventGroups is None):
          if isinstance(eventGroups, types.StringTypes):
            self.eventBroker.removeGroupFromEvent(eventID, eventGroups)
          else:
            for groupID in eventGroups:
              self.eventBroker.removeGroupFromEvent(eventID, groupID, False)
            self.eventBroker.doCommit(True)
      return self.returnAjaxOK()
    except BrokerException as e:
      self.getLogger().fatal(e)
      return "Error {0}".format(e)

  @cherrypy.expose
  @require(requireReferer(('/internal')))
  def modifySubGroups(self, eventID, operation, remainingGroups=None,
                     eventGroups=None):
    """
    modifies the relation between a user and his groups

    :param eventID: The eventID of the event
    :type eventID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingGroups: The identifiers of the groups which the event is
                            not attributed to
    :type remainingGroups: Integer array
    :param eventGroups: The identifiers of the groups which the event is
                       attributed to
    :type eventGroups: Integer array

    :returns: generated HTML
    """
    # right checks
    event = self.eventBroker.getByID(eventID)
    self.checkIfViewable(event)

    try:
      if operation == 'add':
        if not (remainingGroups is None):
          if isinstance(remainingGroups, types.StringTypes):
            self.eventBroker.addSubGroupToEvent(eventID, remainingGroups)
          else:
            for groupID in remainingGroups:
              self.eventBroker.addSubGroupToEvent(eventID, groupID, False)
            self.eventBroker.doCommit(True)
      else:
        if not (eventGroups is None):
          if isinstance(eventGroups, types.StringTypes):
            self.eventBroker.removeSubGroupFromEvent(eventID, eventGroups)
          else:
            for groupID in eventGroups:
              self.eventBroker.removeSubGroupFromEvent(eventID, groupID, False)
            self.eventBroker.doCommit(True)
      return self.returnAjaxOK()
    except BrokerException as e:
      self.getLogger().fatal(e)
      return "Error {0}".format(e)
