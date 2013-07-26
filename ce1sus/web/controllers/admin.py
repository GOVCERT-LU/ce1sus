from ce1sus.web.controllers.base import BaseController
from ce1sus.brokers.classes.permissions import User, Group

import cherrypy
from ce1sus.brokers.permissionbroker import UserBroker, GroupBroker
from ce1sus.brokers.definitionbroker import DEF_ObjectBroker, \
  DEF_AttributeBroker
from ce1sus.brokers.classes.definitions import DEF_Object, DEF_Attribute
import hashlib
import sqlalchemy.exc

class AdminController(BaseController):

  def __init__(self):
    BaseController.__init__(self)
    self.userBroker = self.brokerFactory(UserBroker)
    self.groupBroker = self.brokerFactory(GroupBroker)
    self.objectBroker = self.brokerFactory(DEF_ObjectBroker)
    self.attributeBroker = self.brokerFactory(DEF_AttributeBroker)

  @cherrypy.expose
  def index(self):
    return self.users()

  @cherrypy.expose
  def users(self, identifier=None, errors=False, failedValUser=None, action=None, errorMsg=None):
    template = self.mako.getTemplate('/admin/users.html')
    users = self.userBroker.getAll()
    if failedValUser is None:
      if identifier is None:
        if (len(users) > 0):
          user = users[0]
        else:
          user = None
      else:
        user = self.userBroker.getByID(identifier)
    else:
      user = failedValUser
    remainingGroups = self.userBroker.getGroupsByUser(user.identifier, False)
    return template.render(users=users, userDetails=user, errors=errors, action=action, remainingGroups=remainingGroups, userGroups=user.groups, errorMsg=errorMsg)

  @cherrypy.expose
  def modifyUser(self, identifier=None, username=None, password=None, email=None, action='insert'):
    errorMsg = None
    user = User()
    if not action == 'insert':
      user.identifier = identifier

    if not action == 'remove':
      user.email = email
      hashedPwd = hashlib.sha1()
      hashedPwd.update(password)
      user.password = hashedPwd.hexdigest()
      user.username = username
      errors = not user.validate()
      if not errors:
        if action == 'insert':
          self.userBroker.insert(user)
        if action == 'update':
          self.userBroker.update(user)
        action = None
    else:
      try:
        self.userBroker.removeByID(user.identifier)
      except sqlalchemy.exc.OperationalError:
        errorMsg = 'Cannot delete user. The user is referenced by elements. Remove his groups instead.'
      action = None
      errors = False
      user = None


    return self.users(errors=errors, failedValUser=user, action=action, errorMsg=errorMsg)

  @cherrypy.expose
  def editGroupsUser(self, userID, operation, remainingGroups=None, userGroups=None):
    if operation == 'add':
      if not (remainingGroups is None):
        for groupID in remainingGroups:
          self.groupBroker.addGroupToUser(userID, groupID);
    else:
      if not (userGroups is None):
        for groupID in userGroups:
          self.groupBroker.removeGroupFromUser(userID, groupID);
    return self.users(identifier=userID)

  @cherrypy.expose
  def groups(self, identifier=None, errors=False, failedValGroup=None, action=None, errorMsg=None):
    template = self.mako.getTemplate('/admin/groups.html')
    groups = self.groupBroker.getAll()
    if failedValGroup is None:
      if identifier is None:
        if (len(groups) > 0):
          group = groups[0]
        else:
          group = None
      else:
        group = self.groupBroker.getByID(identifier)
    else:
      group = failedValGroup
    if not group is None:
      remUsers = self.groupBroker.getUsersByGroup(group.identifier, False)
      users = group.users
    else:
      remUsers = None
      users = None
    return template.render(groups=groups, groupDetails=group, errors=errors, action=action, remainingUsers=remUsers, groupUsers=users, errorMsg=errorMsg)

  @cherrypy.expose
  def modifyGroup(self, identifier=None, name=None, shareTLP=0, action='insert'):
    errorMsg = None
    group = Group()
    if not action == 'insert':
      group.identifier = identifier
    if not action == 'remove':
      group.name = name
      group.shareTLP = shareTLP
      errors = not group.validate()
      if not errors:
        if action == 'insert':
          self.groupBroker.insert(group)
        if action == 'update':
          self.groupBroker.update(group)
        action = None
    else:
      try:
        self.groupBroker.removeByID(group.identifier)
        group = None
      except sqlalchemy.exc.OperationalError:
        errorMsg = 'Cannot delete this group. The group is still referenced.'
      action = None
      errors = False

    return self.groups(errors=errors, failedValGroup=group, action=action, errorMsg=errorMsg)

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
  def objects(self, identifier=None, errors=False, failedValObject=None, action=None, errorMsg=None):
    template = self.mako.getTemplate('/admin/objects.html')

    objects = self.objectBroker.getAll()
    if failedValObject is None:
      if identifier is None:
        if (len(objects) > 0):
          obj = objects[0]
        else:
          obj = None
      else:
        obj = self.objectBroker.getByID(identifier)
    else:
      obj = failedValObject

    remainingAttributes = self.objectBroker.getAttributesByObject(obj.identifier, False)
    return template.render(objects=objects, objectDetails=obj, errors=errors, action=action, remainingAttributes=remainingAttributes, objectAttributes=obj.attributes, errorMsg=errorMsg)

  @cherrypy.expose
  def modifyObject(self, identifier=None, name=None, description=None, action='insert'):
    errorMsg = None
    obj = DEF_Object()
    if not action == 'insert':
      obj.identifier = identifier
    if not action == 'remove':
      obj.name = name
      obj.description = description
      errors = not obj.validate()
      if not errors:
        if action == 'insert':
          self.objectBroker.insert(obj)
        if action == 'update':
          self.objectBroker.update(obj)
        action = None
    else:
      try:
        self.objectBroker.removeByID(obj.identifier)
        obj = None
      except sqlalchemy.exc.OperationalError:
        errorMsg = 'Cannot delete this object. The object is still referenced.'

      action = None
      errors = False
    return self.objects(errors=errors, failedValObject=obj, action=action, errorMsg=errorMsg)


  @cherrypy.expose
  def attributes(self, identifier=None, errors=False, failedValAttribute=None, action=None, errorMsg=None):
    template = self.mako.getTemplate('/admin/attributes.html')

    attributes = self.attributeBroker.getAll()
    if failedValAttribute is None:
      if identifier is None:
        if (len(attributes) > 0):
          attribute = attributes[0]
        else:
          attribute = None
      else:
        attribute = self.attributeBroker.getByID(identifier)
    else:
      attribute = failedValAttribute

    remainingAttributes = self.attributeBroker.getObjectsByAttribute(attribute.identifier, False)
    return template.render(attributes=attributes, attributeDetails=attribute, errors=errors,
                           action=action, cbValues=DEF_Attribute.getTableDefinitions(),
                           remainingObjects=remainingAttributes,
                           attributeObjects=attribute.objects, errorMsg=errorMsg)


  @cherrypy.expose
  def modifyAttribute(self, identifier=None, name=None, description='None given', regex='^.*$', classIndex=0, action='insert'):
    errorMsg = None
    attribute = DEF_Attribute()
    if not action == 'insert':
      attribute.identifier = identifier
    if not action == 'remove':
      attribute.name = name
      attribute.description = description
      attribute.classIndex = classIndex
      attribute.regex = regex
      errors = not attribute.validate()
      if not errors:
        if action == 'insert':
          self.attributeBroker.insert(attribute)
        if action == 'update':
          self.attributeBroker.update(attribute)
        action = None
    else:
      try:
        self.attributeBroker.removeByID(attribute.identifier)
        attribute = None
      except sqlalchemy.exc.OperationalError:
        errorMsg = 'Cannot delete this attribute. The attribute is still referenced.'
      action = None
      errors = False
    return self.attributes(errors=errors, failedValAttribute=attribute, action=action, errorMsg=errorMsg)

  @cherrypy.expose
  def editObjectAttribute(self, objID, operation, objectAttributes=None, remainingAttributes=None):
    if operation == 'add':
      if not (remainingAttributes is None):
        for attribute in remainingAttributes:
          self.objectBroker.addAttributeToObject(attribute, objID);
    else:
      if not (objectAttributes is None):
        for attribute in objectAttributes:
          self.objectBroker.removeAttributeFromObject(attribute, objID);
    return self.objects(identifier=objID)


  @cherrypy.expose
  def editAttributeObject(self, AttrID, operation, attributeObjects=None, remainingObjects=None):
    if operation == 'add':
      if not (remainingObjects is None):
        for obj in remainingObjects:
          self.attributeBroker.addObjectToAttribute(obj, AttrID);
    else:
      if not (attributeObjects is None):
        for obj in attributeObjects:
          self.attributeBroker.removeObjectFromAttribute(obj, AttrID);
    return self.attributes(identifier=AttrID)
