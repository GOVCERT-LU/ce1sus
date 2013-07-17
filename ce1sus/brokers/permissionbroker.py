from ce1sus.db.dbexceptions import NothingFoundException
from sqlalchemy.sql.expression import or_
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on Jul 4, 2013

from ce1sus.db.broker import BrokerBase
from ce1sus.brokers.classes.permissions import Group, User, RelationUserGrups
import sqlalchemy.orm.exc

class GroupBroker(BrokerBase):

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return Group

  def getUsersByGroup(self, identifier, belongIn=True):
    try:
      if belongIn:
        result = self.session.query(User).join(RelationUserGrups, Group).filter(Group.identifier == identifier).all()
      else:
        result = self.session.query(User).outerjoin(RelationUserGrups, Group).filter(or_(Group.identifier != identifier, Group.identifier == None)).all()
    except sqlalchemy.orm.exc.NoResultFound:
      result = list()
    return result

  def addGroupToUser(self, userID, groupID):
    try:
      group = self.session.query(Group).filter(Group.identifier == groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    group.addUser(user)
    self.session.commit()

  def removeGroupFromUser(self, userID, groupID):
    try:
      group = self.session.query(Group).filter(Group.identifier == groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    group.removeUser(user)
    self.session.commit()


class UserBroker(BrokerBase):

  def getBrokerClass(self):
    """
    overrides BrokerBase.getBrokerClass
    """
    return User

  def getGroupsByUser(self, identifier, belongIn=True):
    try:
      result = self.session.query(Group).join(RelationUserGrups, User).filter(User.identifier == identifier).all()
      if not belongIn:
        result = self.session.query(Group).filter(~Group.identifier.in_(result))
    except sqlalchemy.orm.exc.NoResultFound:
      result = list()
    return result

  def addUserToGroup(self, userID, groupID):
    try:
      group = self.session.query(Group).filter(Group.identifier == groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    user.addGroup(group)
    self.session.commit()

  def removeUserFromGroup(self, userID, groupID):
    try:
      group = self.session.query(Group).filter(Group.identifier == groupID).one()
      user = self.session.query(User).filter(User.identifier == userID).one()
    except sqlalchemy.orm.exc.NoResultFound:
      raise NothingFoundException('Group or user not found')
    user.removeGroup(group)
    self.session.commit()


