# -*- coding: utf-8 -*-

"""
module handing the groups pages

Created: Aug 19, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from dagr.db.broker import BrokerException, ValidationException, IntegrityException
import types as types
from ce1sus.brokers.staticbroker import TLPLevel
from ce1sus.brokers.permission.permissionclasses import Group
from dagr.controllers.base import ControllerException
from ce1sus.brokers.permission.subgroupbroker import SubGroupBroker
from dagr.helpers.strings import cleanPostValue
from dagr.helpers.converters import ObjectConverter


class GroupController(Ce1susBaseController):
  """Controller handling all the requests for groups"""

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.subgroup_broker = self.broker_factory(SubGroupBroker)

  def get_all_groups(self):
    try:
      return self.group_broker.get_all(Group.name.asc())
    except BrokerException as error:
      self._raise_exception(error)

  def get_group_by_id(self, group_id):
    try:
      return self.group_broker.get_by_id(group_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_available_subgroups(self, group):
    try:
      return self.group_broker.get_subgroups_by_group(group.identifier,
                                                          False)
    except BrokerException as error:
      self._raise_exception(error)

  def get_cb_tlp_lvls(self):
    try:
      return TLPLevel.get_definitions()
    except BrokerException as error:
      self._raise_exception(error)

  @staticmethod
  def __handle_input(add_function, object_id, value):
    if value:
      if isinstance(value, types.StringTypes):
        add_function(object_id, value, False)
      else:
        for attribute_id in value:
          add_function(object_id, attribute_id, False)

  def modify_group_subgroup_relations(self, operation, group_id, remaining_subgroups, group_subgroups):
    try:
      if operation == 'add':
        GroupController.__handle_input(self.group_broker.add_subgroup_to_group,
                                           group_id, remaining_subgroups)
      else:
        GroupController.__handle_input(self.group_broker.remove_subgroup_from_group,
                                           group_id, group_subgroups)
      self.group_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)

  def populate_group(self,
                     identifier,
                     name,
                     description,
                     download,
                     action,
                     tlp_lvl,
                     email,
                     usermails):
    group = Group()
    if not action == 'insert':
      group = self.group_broker.get_by_id(identifier)
    if not action == 'remove':
      group.name = cleanPostValue(name)
      group.email = cleanPostValue(email)
      ObjectConverter.set_integer(group, 'can_download', download)
      ObjectConverter.set_integer(group, 'tlp_lvl', tlp_lvl)
      ObjectConverter.set_integer(group, 'usermails', usermails)
      group.description = cleanPostValue(description)
    return group

  def insert_group(self, group):
    try:
      default_subgroup = self.subgroup_broker.get_by_id(1)
      group.subgroups.append(default_subgroup)
      self.group_broker.insert(group)
      return group, True
    except ValidationException as error:
      return group, False
    except BrokerException as error:
      self._raise_exception(error)

  def update_group(self, group):
    try:
      self.group_broker.update(group)
      return group, True
    except ValidationException as error:
      return group, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_group(self, group):
    try:
      self.group_broker.remove_by_id(group.identifier)
      return group, True
    except IntegrityException as error:
      raise ControllerException('Cannot delete this group. The group is referenced by elements.'
                    + ' Remove the events of this group first.')
    except BrokerException as error:
      self._raise_exception(error)
