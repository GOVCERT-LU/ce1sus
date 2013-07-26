'''
Created on Jul 3, 2013

@author: jhemp
'''


from sqlalchemy import Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.types import DateTime
from ce1sus.db.session import Base
import ce1sus.helpers.validator as validator

# Relation table for user and groups

# ass net agebonnen mai ouni geet et net!?
__RelationUserGrups = Table(
    'User_has_Groups', Base.metadata,
    Column('user_id', Integer, ForeignKey('Users.user_id')),
    Column('group_id', Integer, ForeignKey('Groups.group_id'))
    )

class User(Base):
  __tablename__ = 'Users'

  identifier = Column('user_id', Integer, primary_key=True)
  username = Column('username', String)
  password = Column('password', String)
  privileged = Column('privileged', Integer)
  last_login = Column('last_login', DateTime)
  email = Column('email', String)

  groups = relationship('Group', secondary='User_has_Groups', back_populates='users', cascade='all')

  def addGroup(self, group):
    self.groups.append(group)

  def removeGroup(self, group):
    self.groups.remove(group)

  def validate(self):
    validator.validateAlNum(self, 'username')
    validator.validateRegex(self, 'password', "^.+$", "fail")
    # validator.validateRegex(self,'privileged', "^[a-z,]*$", "fail")
    validator.validateEmailAddress(self, 'email')
    return validator.isObjectValid(self)

class Group(Base):
  __tablename__ = 'Groups'

  identifier = Column('group_id', Integer, primary_key=True)
  name = Column('name', String)
  shareTLP = Column('auto_share_tlp', Integer)
  users = relationship(User, secondary='User_has_Groups', back_populates='groups', cascade='all')

  def __str__(self):
    return str(self.__dict__)

  def addUser(self, user):
    self.users.append(user)

  def removeUser(self, user):
    self.users.remove(user)

  def validate(self):
    validator.validateAlNum(self, 'name')
    validator.validateDigits(self, 'shareTLP')
    return validator.isObjectValid(self)
