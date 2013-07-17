from ce1sus.web.controllers.base import BaseController
from ce1sus.brokers.classes.permissions import User, Group

import cherrypy
from ce1sus.brokers.permissionbroker import UserBroker, GroupBroker
from sqlalchemy import types


class AdminController(BaseController):

  def __init__(self):
    BaseController.__init__(self)
    self.userBroker = self.brokerFactory(UserBroker)
    self.groupBroker = self.brokerFactory(GroupBroker)

  @cherrypy.expose
  def index(self):
    return self.users()

  @cherrypy.expose
  def users(self, identifier=None, errors=False, failUser=None, addUser=False):
    template = self.mako.getTemplate('/index/admin/users.html')

    users = self.userBroker.getAll()
    if failUser is None:
      if identifier is None:
        if (len(users) > 0):
          user = users[0]
        else:
          user = None
      else:
        user = self.userBroker.getByID(identifier)
    else:
      user = failUser
    remainingGroups = self.userBroker.getGroupsByUser(user.identifier, False)
    return template.render(users=users, userDetails=user, errors=errors, addUser=addUser, remainingGroups=remainingGroups, userGroups=user.groups)

  @cherrypy.expose
  def addUser(self, identifier=None, username=None, password=None, email=None):
    user = User()
    user.email = email
    user.password = password
    user.username = username
    errors = not user.validate()
    if not errors:
      self.userBroker.insert(user)
    return self.users(errors=errors, failUser=user, addUser=True)

  @cherrypy.expose
  def editUser(self, identifier=None, username=None, password=None, email=None):

    user = User()
    user.identifier = identifier
    user.email = email
    user.password = password
    user.username = username
    errors = not user.validate()
    if not errors:
      self.userBroker.update(user)
    return self.users(errors=errors, failUser=user, addUser=False)

  @cherrypy.expose
  def groups(self, identifier=None, errors=False, failGroup=None, addGroup=False):
    template = self.mako.getTemplate('/index/admin/groups.html')

    groups = self.groupBroker.getAll()
    if failGroup is None:
      if identifier is None:
        if (len(groups) > 0):
          group = groups[0]
        else:
          group = None
      else:
        group = self.groupBroker.getByID(identifier)
    else:
      group = failGroup

    remUsers = self.groupBroker.getUsersByGroup(group.identifier, False)

    return template.render(groups=groups, groupDetails=group, errors=errors, addGroup=addGroup, remainingUsers=remUsers, groupUsers=group.users)

  @cherrypy.expose
  def addGroup(self, identifier=None, name=None, shareTLP=0):
    group = Group()
    group.name = name
    group.shareTLP = shareTLP
    errors = not group.validate()
    if not errors:
      self.groupBroker.insert(group)
    return self.groups(errors=errors, failGroup=group, addGroup=True)

  @cherrypy.expose
  def editUserGroups(self, groupID, operation, groupUsers=None, remainingUsers=None):
    if operation == 'add':
      if not (remainingUsers is None):
        for userID in remainingUsers:
          self.userBroker.addUserToGroup(userID, groupID);
    else:
      if not (groupUsers is None):
        for userID in groupUsers:
          self.userBroker.removeUserFromGroup(userID, groupID);
    return self.groups(identifier=groupID)

  @cherrypy.expose
  def objects(self):
    template = self.mako.getTemplate('/index/admin/objects.html')
    return template.render()

  @cherrypy.expose
  def attributes(self):
    template = self.mako.getTemplate('/index/admin/attributes.html')
    return template.render()
