# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, IntegrityException
import sqlalchemy.orm.exc
from dagr.db.broker import BrokerException
from ce1sus.brokers.permission.permissionclasses import Group, SubGroup


class SubGroupBroker(BrokerBase):
  """This is the interface between python an the database"""

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return SubGroup

  def get_groups_by_subgroup(self, identifier, belong_in=True):
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
      groups = self.session.query(Group).join(SubGroup.groups).filter(SubGroup.identifier == identifier).order_by(Group.name).all()
      if not belong_in:
        group_ids = list()
        for subgroup in groups:
          group_ids.append(subgroup.identifier)
        groups = self.session.query(Group).filter(~Group.identifier.in_(group_ids)).order_by(Group.name).all()
      return groups
    except sqlalchemy.orm.exc.NoResultFound:
      return list()
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def add_group_to_subgroup(self, subgroup_id, group_id, commit=True):
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
      subgroup.groups.append(group)
      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Group or subgroup not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def remove_group_from_subgroup(self, subgroup_id, group_id, commit=True):
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
      subgroup.groups.remove(group)
      self.do_commit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException(u'Group or subgroup not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def remove_by_id(self, subgroup_id, commit=True):
    if subgroup_id == 1 or subgroup_id == '1':
      raise IntegrityException(u'Cannot delete this subgroup. The subgroup is essential to the application.')
    else:
      BrokerBase.remove_by_id(self, subgroup_id, commit)
