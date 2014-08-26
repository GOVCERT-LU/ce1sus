# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, BrokerException, IntegrityException, TooManyResultsFoundException
import sqlalchemy.orm.exc
from ce1sus.brokers.permission.permissionclasses import Group, SubGroup


class GroupBroker(BrokerBase):
  """This is the interface between python an the database"""

  def get_broker_class(self):
    """
    overrides BrokerBase.get_broker_class
    """
    return Group

  def get_by_uuid(self, uuid):
    try:

      result = self.session.query(self.get_broker_class()).filter(Group.uuid == uuid).one()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with uuid :{0}'.format(uuid))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for uuid :{0}'.format(uuid))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

  def get_by_name(self, name):
    try:

      result = self.session.query(self.get_broker_class()).filter(Group.name == name).one()
      return result
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found with name :{0}'.format(name))
    except sqlalchemy.orm.exc.MultipleResultsFound:
      raise TooManyResultsFoundException('Too many results found for name :{0}'.format(name))
    except sqlalchemy.exc.SQLAlchemyError as error:
      raise BrokerException(error)

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
      subgroups = self.session.query(SubGroup).join(Group.subgroups).filter(Group.identifier == identifier).order_by(SubGroup.name).all()
      if not belong_in:
        subgroups_ids = list()
        for subgroup in subgroups:
          subgroups_ids.append(subgroup.identifier)
        subgroups = self.session.query(SubGroup).filter(~SubGroup.identifier.in_(subgroups_ids)).order_by(SubGroup.name).all()
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
      raise NothingFoundException(u'Group or subgroup not found')
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
      raise NothingFoundException(u'Group or user not found')
    except sqlalchemy.exc.SQLAlchemyError as error:
      self.session.rollback()
      raise BrokerException(error)

  def remove_by_id(self, group_id, commit=True):
    if group_id == 1 or group_id == '1':
      raise IntegrityException(u'Cannot delete this group. The group is essential to the application.')
    else:
      BrokerBase.remove_by_id(self, group_id, commit)
