# -*- coding: utf-8 -*-

"""
module handing the groups pages

Created: Nov 5, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.controllers.base import Ce1susBaseController
from dagr.db.broker import BrokerException, ValidationException
import types as types
from ce1sus.brokers.staticbroker import TLPLevel
from ce1sus.brokers.permission.subgroupbroker import SubGroupBroker
from ce1sus.brokers.permission.permissionclasses import SubGroup
from dagr.helpers.strings import cleanPostValue


class SubGroupController(Ce1susBaseController):

  def __init__(self, config):
    Ce1susBaseController.__init__(self, config)
    self.subgroup_broker = self.broker_factory(SubGroupBroker)

  def get_all_subgroups(self):
    try:
      return self.subgroup_broker.get_all(SubGroup.name.asc())
    except BrokerException as error:
      self._raise_exception(error)

  def get_subgroup_by_id(self, subgroup_id):
    try:
      return self.subgroup_broker.get_by_id(subgroup_id)
    except BrokerException as error:
      self._raise_exception(error)

  def get_available_subgroups(self, subgroup):
    try:
      return self.subgroup_broker.get_groups_by_subgroup(subgroup.identifier,
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

  def modify_subgroup_group_relations(self, operation, group_id, remaining_subgroups, group_subgroups):
    try:
      if operation == 'add':
        SubGroupController.__handle_input(self.subgroup_broker.add_group_to_subgroup,
                                           group_id, remaining_subgroups)
      else:
        SubGroupController.__handle_input(self.subgroup_broker.remove_group_from_subgroup,
                                           group_id, group_subgroups)
      self.subgroup_broker.do_commit(True)
    except BrokerException as error:
      self._raise_exception(error)

  def populate_subgroup(self,
                        identifier,
                        name,
                        description,
                        action):
    subgroup = SubGroup()
    if not action == 'insert':
      subgroup = self.subgroup_broker.get_by_id(identifier)
    if not action == 'remove':
      subgroup.name = cleanPostValue(name)
      subgroup.description = cleanPostValue(description)
    return subgroup

  def insert_group(self, subgroup):
    try:
      self.subgroup_broker.insert(subgroup)
      return subgroup, True
    except ValidationException as error:
      return subgroup, False
    except BrokerException as error:
      self._raise_exception(error)

  def update_group(self, subgroup):
    try:
      self.subgroup_broker.update(subgroup)
      return subgroup, True
    except ValidationException as error:
      return subgroup, False
    except BrokerException as error:
      self._raise_exception(error)

  def remove_group(self, subgroup):
    try:
      self.subgroup_broker.remove_by_id(subgroup.identifier)
      return subgroup, True
    except BrokerException as error:
      self._raise_exception(error)
