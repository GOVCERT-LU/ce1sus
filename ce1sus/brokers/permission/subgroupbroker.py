# -*- coding: utf-8 -*-

"""This module provides container classes and interfaces
for inserting data into the database.

Created on Jul 4, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.db.broker import BrokerBase, NothingFoundException
import sqlalchemy.orm.exc
from dagr.db.broker import BrokerException
from ce1sus.brokers.permission.permissionclasses import Group, SubGroup


class SubGroupBroker(BrokerBase):
  """This is the interface between python an the database"""

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return SubGroup

  def getGroupsBySubGroup(self, identifier, belongIn=True):
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
      groups = self.session.query(Group).join(SubGroup.groups).filter(
                                              SubGroup.identifier == identifier
                                                                      ).all()
      if not belongIn:
        groupIDs = list()
        for subgroup in groups:
          groupIDs.append(subgroup.identifier)
        groups = self.session.query(Group).filter(~Group.identifier.in_(
                                                                  groupIDs
                                                                            )
                                                        )
      return groups
    except sqlalchemy.orm.exc.NoResultFound:
      return list()
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def addGroupToSubGroup(self, groupID, subGroupID, commit=True):
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
      subgroup.groups.append(group)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or subgroup not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  def removeSubGroupFromGroup(self, groupID, subGroupID, commit=True):
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
      subgroup.groups.remove(group)
      self.doCommit(commit)
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or subgroup not found')
    except sqlalchemy.exc.SQLAlchemyError as e:
      self.getLogger().fatal(e)
      self.session.rollback()
      raise BrokerException(e)

  # pylint: disable=R0903,R0913
  @staticmethod
  def buildSubGroup(identifier=None,
                 name=None,
                 description=None,
                 action='insert'):
    """
    puts a subgroup with the data together

    :param identifier: The identifier of the subgroup,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the subgroup
    :type name: String
    :param description: The description of this subgroup
    :type description: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: Group
    """
    subgroup = SubGroup()
    if not action == 'insert':
      subgroup.identifier = identifier
    if not action == 'remove':
      subgroup.name = name.strip()
      subgroup.description = description.strip()
    return subgroup
