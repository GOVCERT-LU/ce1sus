# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException, BrokerException
import sqlalchemy.orm.exc
from dagr.helpers.converters import ObjectConverter
from ce1sus.brokers.permission.permissionclasses import Group, SubGroup
from dagr.helpers.strings import cleanPostValue


class GroupBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Group

  def getSubGroupsByGroup(self, identifier, belongIn=True):
    """
    get all users in a given group

    :param identifier: identifier of the group
    :type identifier: Integer
    :param belongIn: If set returns all the attributes of the object else
                     all the attributes not belonging to the object
    :type belongIn: Boolean

    :returns: list of Users
    """
    try:
      subgroups = self.session.query(SubGroup).join(Group.subgroups).filter(
                                        Group.identifier == identifier
                                        ).order_by(SubGroup.name).all()
      if not belongIn:
        subgroupsIDs = list()
        for subgroup in subgroups:
          subgroupsIDs.append(subgroup.identifier)
        subgroups = self.session.query(SubGroup).filter(
 ~SubGroup.identifier.in_(
                            subgroupsIDs
                          )
                          ).order_by(SubGroup.name).all()
      return subgroups
    except sqlalchemy.orm.exc.NoResultFound:
      return list()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def addSubGroupToGroup(self, subGroupID, groupID, commit=True):
    """
    Add a user to a group

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      subgroup = self.session.query(SubGroup).filter(SubGroup.identifier
                                                     == subGroupID).one()
      group.subgroups.append(subgroup)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or subgroup not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeSubGroupFromGroup(self, subGroupID, groupID, commit=True):
    """
    Removes a user to a group

    :param userID: Identifier of the user
    :type userID: Integer
    :param groupID: Identifier of the group
    :type groupID: Integer
    """
    try:
      group = self.session.query(Group).filter(Group.identifier ==
                                               groupID).one()
      subgroup = self.session.query(SubGroup).filter(SubGroup.identifier
                                                     == subGroupID).one()
      group.subgroups.remove(subgroup)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  # pylint: disable=R0903,R0913
  @staticmethod
  def buildGroup(identifier=None,
                 name=None,
                 description=None,
                 download=None,
                 action='insert',
                 tlpLvl=None,
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
      group.identifier = identifier
    if not action == 'remove':
      group.name = cleanPostValue(name)
      group.email = cleanPostValue(email)
      ObjectConverter.setInteger(group, 'canDownload', download)
      ObjectConverter.setInteger(group, 'tlpLvl', tlpLvl)
      ObjectConverter.setInteger(group, 'usermails', usermails)
      group.description = cleanPostValue(description)
    return group

  def getAll(self):
    """
    Returns all getBrokerClass() instances

    Note: raises a NothingFoundException or a TooManyResultsFound Exception

    :returns: list of instances
    """
    try:
      result = self.session.query(self.getBrokerClass()
                                  ).order_by(Group.name.asc()).all()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Nothing found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      raise BrokerException(e)

    return result
