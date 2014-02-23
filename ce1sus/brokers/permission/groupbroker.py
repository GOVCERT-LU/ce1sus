# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, BrokerException, IntegrityException
import sqlalchemy.orm.exc
from dagr.helpers.converters import ObjectConverter
from ce1sus.brokers.permission.permissionclasses import Group, SubGroup
from dagr.helpers.strings import cleanPostValue


class GroupBroker(BrokerBase):
  """This is the interface between python an the database"""

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Group

  def get_subgroups_by_group(self, identifier, belong_in=True):
    """
    get all users in a given group

    :param identifier: identifier of the group
    :type identifier: Integer
    :param belong_in: If set returns all the attributes of the object else
                     all the attributes not belonging to the object
    :type belong_in: Boolean

    :returns: list of Users
    """
    try:
      subgroups = self.session.query(SubGroup).join(Group.subgroups).filter(
                                        Group.identifier == identifier
                                        ).order_by(SubGroup.name).all()
      if not belong_in:
        subgroups_ids = list()
        for subgroup in subgroups:
          subgroups_ids.append(subgroup.identifier)
        subgroups = self.session.query(SubGroup).filter(
 ~SubGroup.identifier.in_(
                            subgroups_ids
                          )
                          ).order_by(SubGroup.name).all()
      return subgroups
    except sqlalchemy.orm.exc.NoResultFound:
      return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def add_subgroup_to_group(self, group_id, subgroup_id, commit=True):
    """
    Add a user to a group

    :param userID: Identifier of the user
    :type userID: Integer
    :param group_id: Identifier of the group
    :type group_id: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               group_id).one()
      subgroup = self.session.query(SubGroup).filter(SubGroup.identifier
                                                     == subgroup_id).one()
      group.subgroups.append(subgroup)
      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or subgroup not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def remove_subgroup_from_group(self, group_id, subgroup_id, commit=True):
    """
    Removes a user to a group

    :param userID: Identifier of the user
    :type userID: Integer
    :param group_id: Identifier of the group
    :type group_id: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               group_id).one()
      subgroup = self.session.query(SubGroup).filter(SubGroup.identifier
                                                     == subgroup_id).one()
      group.subgroups.remove(subgroup)
      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  # pylint: disable=R0903,R0913
  def build_group(self,
                 identifier=None,
                 name=None,
                 description=None,
                 download=None,
                 action='insert',
                 tlp_lvl=None,
                 email=None,
                 usermails=None):
    """
    puts a group with the data together

    :param identifier: The identifier of the group,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the group
    :type name: String
    :param description: The description of this group
    :type description: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: Group
    """
    group = Group()
    if not action == 'insert':
      group = self.get_by_id(identifier)
    if not action == 'remove':
      group.name = cleanPostValue(name)
      group.email = cleanPostValue(email)
      ObjectConverter.set_integer(group, 'can_download', download)
      ObjectConverter.set_integer(group, 'tlp_lvl', tlp_lvl)
      ObjectConverter.set_integer(group, 'usermails', usermails)
      group.description = cleanPostValue(description)
    return group

  def remove_by_id(self, group_id, commit=True):
    if group_id == 1 or group_id == '1':
      raise IntegrityException('Cannot delete this group. The group is essential to '
                  + 'the application.')
    else:
      BrokerBase.remove_by_id(self, group_id, commit)
