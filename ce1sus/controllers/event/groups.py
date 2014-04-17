# -*- coding: utf-8 -*-

"""
module handing the group pages

Created: Aug 21, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
import types
from dagr.db.broker import BrokerException


class GroupsController(Ce1susBaseController):
  """event controller handling all actions in the event section"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)

  def get_available_groups(self, event):
    try:
      return self.event_broker.get_event_groups(event.identifier, False)
    except BrokerException as error:
      self._raise_exception(error)

  def get_available_subgroups(self, event):
    try:
      return self.event_broker.get_event_subgroups(event.identifier, False)
    except BrokerException as error:
      self._raise_exception(error)

  @staticmethod
  def __handle_input(add_function, event_id, post_value):
    if post_value:
      if isinstance(post_value, types.StringTypes):
        add_function(event_id, post_value, False)
      else:
        for group_id in post_value:
          add_function(event_id, group_id, False)

  def modify_groups(self, operation, event_id, remaining_groups, event_groups):
    try:
      if operation == 'add':
        GroupsController.__handle_input(self.event_broker.add_group_to_event, event_id, remaining_groups)
      else:
        GroupsController.__handle_input(self.event_broker.remove_group_from_event, event_id, event_groups)
      self.event_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)

  def modify_subgroups(self, operation, event_id, remaining_subgroups, event_subgroups):
    try:
      if operation == 'add':
        GroupsController.__handle_input(self.event_broker.add_subgroup_to_event, event_id, remaining_subgroups)
      else:
        GroupsController.__handle_input(self.event_broker.remove_subgroup_from_event, event_id, event_subgroups)
      self.event_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)
