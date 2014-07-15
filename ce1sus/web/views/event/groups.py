# -*- coding: utf-8 -*-

"""
(Description)

Created on Feb 3, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


from ce1sus.web.views.base import Ce1susBaseView
from ce1sus.controllers.event.groups import GroupsController
import cherrypy
from ce1sus.web.views.common.decorators import require, require_referer
from dagr.controllers.base import ControllerException
import types


class GroupsView(Ce1susBaseView):
  """index view handling all display in the index section"""

  def tabs(self):
    return [('Groups', 1, '/events/event/groups/groups', 'reload')]

  def __init__(self, config):
    Ce1susBaseView.__init__(self, config)
    self.groups_controller = GroupsController(config)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  @cherrypy.tools.allow(methods=['GET'])
  def groups(self, event_id):
    try:
      event = self.groups_controller.get_event_by_id(event_id)
      # the user can only change the groups if he is the owner
      self._check_if_event_owner(event)
      remaining_groups = self.groups_controller.get_available_groups(event)
      remaining_subgroups = self.groups_controller.get_available_subgroups(event)

      return self._render_template('/events/event/groups/groups.html',
                                   remaining_groups=remaining_groups,
                                   event=event,
                                   remaining_subgroups=remaining_subgroups,
                                   owner=self._is_event_owner(event),
                                   enabled=True)

    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  # @cherrypy.tools.allow(methods=['POST'])
  def modify_groups(self, identifier, operation, remaining=None, existing=None):
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
    try:
      self._check_if_valid_operation(operation)
      event = self.groups_controller.get_event_by_id(identifier)
      self._check_if_event_owner(event)
      self.groups_controller.modify_groups(operation, identifier, remaining, existing)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)

  @cherrypy.expose
  @require(require_referer(('/internal')))
  @cherrypy.tools.allow(methods=['POST'])
  def modify_subgroups(self, identifier, operation, remaining=None, existing=None):
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
    try:
      self._check_if_valid_operation(operation)
      event = self.groups_controller.get_event_by_id(identifier)
      self._check_if_event_owner(event)
      self.groups_controller.modify_subgroups(operation, identifier, remaining, existing)
      return self._return_ajax_ok()
    except ControllerException as error:
      return self._render_error_page(error)
