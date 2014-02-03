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
from ce1sus.web.helpers.protection import require, require_referer
import types
from dagr.db.broker import BrokerException
from ce1sus.brokers.event.eventbroker import EventBroker


class GroupsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.event_broker = self.broker_factory(EventBroker)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  def maingroups(self, eventID):
    """
    Event page listing
    """
    template = self.mako._get_template('/events/event/groups/groups.html')
    event = self.event_broker.get_by_id(eventID)
    # right checks
    if self.isAdminArea():
      self.checkIfPriviledged(self.get_user(True))
    else:
      self.checkIfViewable(event, self.get_user(True))
    remainingGroups = self.event_broker.get_event_groups(event.identifier,
                                                        False)
    remainingSubGroups = self.event_broker.get_event_subgroups(event.identifier,
                                                           False)

    return self.clean_html_code(template.render(event_id=event.identifier,
                           remainingGroups=remainingGroups,
                           eventGroups=event.maingroups,
                           remainingSubGroups=remainingSubGroups,
                           eventSubGroups=event.subgroups,
                           owner=self.is_event_owner(event, self.get_user(True))))

  @cherrypy.expose
  @require(require_referer(('/internal')))
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
    event = self.event_broker.get_by_id(eventID)
    if self.isAdminArea():
      self.checkIfPriviledged(self.get_user(True))
    else:
      self.checkIfViewable(event, self.get_user(True))

    try:
      if operation == 'add':
        if not (remainingGroups is None):
          if isinstance(remainingGroups, types.StringTypes):
            self.event_broker.add_group_to_event(eventID, remainingGroups)
          else:
            for groupID in remainingGroups:
              self.event_broker.add_group_to_event(eventID, groupID, False)
            self.event_broker.do_commit(True)
      else:
        if not (eventGroups is None):
          if isinstance(eventGroups, types.StringTypes):
            self.event_broker.remove_group_from_event(eventID, eventGroups)
          else:
            for groupID in eventGroups:
              self.event_broker.remove_group_from_event(eventID, groupID, False)
            self.event_broker.do_commit(True)
      return self._return_ajax_ok()
    except BrokerException as e:
      self._get_logger().fatal(e)
      return "Error {0}".format(e)

  @cherrypy.expose
  @require(require_referer(('/internal')))
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
    event = self.event_broker.get_by_id(eventID)
    self.checkIfViewable(event, self.get_user(True))

    try:
      if operation == 'add':
        if not (remainingGroups is None):
          if isinstance(remainingGroups, types.StringTypes):
            self.event_broker.add_subgroup_to_event(eventID, remainingGroups)
          else:
            for groupID in remainingGroups:
              self.event_broker.add_subgroup_to_event(eventID, groupID, False)
            self.event_broker.do_commit(True)
      else:
        if not (eventGroups is None):
          if isinstance(eventGroups, types.StringTypes):
            self.event_broker.remove_subgroup_from_event(eventID, eventGroups)
          else:
            for groupID in eventGroups:
              self.event_broker.remove_subgroup_from_event(eventID, groupID, False)
            self.event_broker.do_commit(True)
      return self._return_ajax_ok()
    except BrokerException as e:
      self._get_logger().fatal(e)
      return "Error {0}".format(e)
