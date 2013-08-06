"""module holding all controllers needed for the administration"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, Weber Jean-Paul'
__license__ = 'GPL v3+'

# Created on July 26, 2013

from ce1sus.web.controllers.base import BaseController
import cherrypy
from ce1sus.brokers.permissionbroker import UserBroker, GroupBroker, User, Group
from ce1sus.brokers.definitionbroker import ObjectDefinitionBroker, \
  AttributeDefinitionBroker, ObjectDefinition, AttributeDefinition
from ce1sus.web.helpers.protection import require, privileged
from ce1sus.web.helpers.pagination import Paginator
from ce1sus.helpers.ldaphandling import LDAPHandler, LDAPException
from ce1sus.db.broker import OperationException, BrokerException, \
  IntegrityException, ValidationException

import types

class AdminController(BaseController):
  """admim controller handling all actions in the admin section"""

  def __init__(self):
    BaseController.__init__(self)
    self.userBroker = self.brokerFactory(UserBroker)
    self.groupBroker = self.brokerFactory(GroupBroker)
    self.objectBroker = self.brokerFactory(ObjectDefinitionBroker)
    self.attributeBroker = self.brokerFactory(AttributeDefinitionBroker)


  @cherrypy.expose
  @require(privileged())
  def index(self):
    """
    index page

    :returns: generated HTML
    """
    return self.users()

# BEGIN USER HANDLING

  @require(privileged())
  @cherrypy.expose
  def users(self, identifier=None, user=None, action=None,
            errorMsg=None):

    """
    renders the user page

    :param identifier: the identifier of the user to show the details
    :type identifier: Integer
    :param user: A specific user to display in the user details
    :type user: User
    :param action: action which is taken (i.e. edit, insert, remove)
                   depending on the case the page is displayed differently
    :type action: String
    :param errorMsg: General error to be displayed
    :type errorMsg: String

    :Note: use either identifier or user (the user parameter has the priority)

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/users.html')
    users = self.userBroker.getAll()
    errors = False
    if user is None:
      if identifier is None:
        if (len(users) > 0):
          user = users[0]
        else:
          user = None
      else:
        user = self.userBroker.getByID(identifier)
    else:
      user = user
      # prevents unnecessary parameter
      errors = not user.validate()
    remainingGroups = self.userBroker.getGroupsByUser(user.identifier, False)
    groups = user.groups

    cbValues = {'No':0, 'Yes':1}

    labels = [{'radio':'#'},
              {'uid':'username'},
              {'mail':'Email'},
              {'displayName':'Name'}
              ]

    lh = LDAPHandler.getInstance()
    lh.open()
    userList = lh.getAllUsers()
    # add radiobutton to list
    for item in userList:
      setattr(item, 'radio',
              '<input type="radio" name="identifier" value="{0}"/>'.format(
                                                                    item.uid))

    ldapPaginator = Paginator(items=userList,
                          labelsAndProperty=labels,
                          baseUrl='/events/tickets',
                          showOptions=False)
    lh.close()



    return template.render(users=users, userDetails=user, errors=errors,
                           action=action, remainingGroups=remainingGroups,
                           userGroups=groups, errorMsg=errorMsg,
                           cbValues=cbValues, LDAPpaginator=ldapPaginator)

  @require(privileged())
  @cherrypy.expose
  def modifyUser(self, identifier=None, username=None, password=None,
                 privileged=None, email=None, action='insert',
                 LDAPUserTable_length=None):
    """
    modifies or inserts a user with the data of the post

    :param identifier: The identifier of the user,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param username: The username of the user
    :type username: String
    :param password: The password of the user
    :type password: String
    :param email: The email of the user
    :type email: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String


    :returns: generated HTML
    """

    errorMsg = None
    user = User()
    if not action == 'insert':
      user.identifier = identifier

    if not action == 'remove':
      user.email = email
      user.password = password
      user.username = username
      user.privileged = privileged

      if action == 'insertLDAP':
        user.identifier = None
        # get LDAP user
        if not identifier is None:
          try:
            lh = LDAPHandler.getInstance()
            lh.open()
            ldapUser = lh.getUser(identifier)
            lh.close()
            user.username = ldapUser.uid
            user.password = ldapUser.password
            user.email = ldapUser.mail
            user.privileged = 0
          except LDAPException as e:
            self.getLogger().error(e)
        else:
          action = None
          user = None

      try:
        if action == 'insert' or action == 'insertLDAP':
          self.userBroker.insert(user)
        if action == 'update':
          self.userBroker.update(user)
        action = None
      except ValidationException:
        self.getLogger().info('User is invalid')
      except BrokerException as e:
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None
        user = None
    else:
      try:
        self.userBroker.removeByID(user.identifier)
      except OperationException:
        errorMsg = ('Cannot delete user. The user is referenced by elements.'
                    + ' Remove his groups instead.')
      action = None
      user = None


    return self.users(user=user, action=action, errorMsg=errorMsg)

  @require(privileged())
  @cherrypy.expose
  def editGroupsUser(self, userID, operation, remainingGroups=None,
                     userGroups=None):
    """
    modifies the relation between a user and his groups

    :param userID: The userID of the user
    :type userID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingGroups: The identifiers of the groups which the user is not
                            attributed to
    :type remainingGroups: Integer array
    :param userGroups: The identifiers of the groups which the user is
                       attributed to
    :type userGroups: Integer array

    :returns: generated HTML
    """

    if operation == 'add':
      if not (remainingGroups is None):
        if isinstance(remainingGroups, types.StringTypes):
          self.groupBroker.addGroupToUser(userID, remainingGroups)
        else:
          for groupID in remainingGroups:
            self.groupBroker.addGroupToUser(userID, groupID, False)
          self.groupBroker.session.commit()
    else:
      if not (userGroups is None):
        if isinstance(userGroups, types.StringTypes):
          self.groupBroker.removeGroupFromUser(userID, userGroups)
        else:
          for groupID in userGroups:
            self.groupBroker.removeGroupFromUser(userID, groupID, False)
          self.groupBroker.session.commit()

    return self.users(identifier=userID)


# END USER HANDLING

# BEGIN GROUP HANDLING

  @require(privileged())
  @cherrypy.expose
  def groups(self, identifier=None, group=None, action=None,
             errorMsg=None):
    """
    renders the group page

    :param identifier: the identifier of the group to show the details
    :type identifier: Integer
    :param group: A specific group to display in the group details
    :type group: Group
    :param action: action which is taken (i.e. edit, insert, remove)
                   depending on the case the page is displayed differently
    :type action: String
    :param errorMsg: General error to be displayed
    :type errorMsg: String

    :Note: use either identifier or group (the group parameter has the priority)

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/groups.html')
    groups = self.groupBroker.getAll()
    errors = False
    if group is None:
      if identifier is None:
        if (len(groups) > 0):
          group = groups[0]
        else:
          group = None
      else:
        group = self.groupBroker.getByID(identifier)
    else:
      group = group
      # prevents unnecessary parameter
      errors = not group.validate()
    if not group is None:
      remUsers = self.groupBroker.getUsersByGroup(group.identifier, False)
      users = group.users
    else:
      remUsers = None
      users = None
    return template.render(groups=groups, groupDetails=group, errors=errors,
                           action=action, remainingUsers=remUsers,
                           groupUsers=users, errorMsg=errorMsg)

  @require(privileged())
  @cherrypy.expose
  def modifyGroup(self, identifier=None, name=None, shareTLP=0,
                  description=None, action='insert'):
    """
    modifies or inserts a group with the data of the post

    :param identifier: The identifier of the group,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the group
    :type name: String
    :param description: The description of this group
    :type description: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    errorMsg = None
    group = Group()
    if not action == 'insert':
      group.identifier = identifier
    if not action == 'remove':
      group.name = name
      group.shareTLP = shareTLP
      group.description = description

      try:
        if action == 'insert':
          self.groupBroker.insert(group)
        if action == 'update':
          self.groupBroker.update(group)
        action = None
      except ValidationException:
        self.getLogger().info('Group is invalid')
      except BrokerException as e:
        self.getLogger().info('An unexpected error occurred: {0}'.format(e))
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None
        group = None

    else:
      try:
        self.groupBroker.removeByID(group.identifier)
        group = None
      except OperationException:
        errorMsg = 'Cannot delete this group. The group is still referenced.'
      action = None

    return self.groups(group=group, action=action, errorMsg=errorMsg)

  @require(privileged())
  @cherrypy.expose
  def editUserGroups(self, groupID, operation,
                     groupUsers=None, remainingUsers=None):
    """
    modifies the relation between a group and its users

    :param groupID: The groupID of the group
    :type groupID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingUsers: The identifiers of the users which the group is not
                            attributed to
    :type remainingUsers: Integer array
    :param groupUsers: The identifiers of the users which the group is
                       attributed to
    :type groupUsers: Integer array

    :returns: generated HTML
    """
    if operation == 'add':
      if not (remainingUsers is None):
        if isinstance(remainingUsers, types.StringTypes):
          self.userBroker.addUserToGroup(remainingUsers, groupID)
        else:
          for userID in remainingUsers:
            self.userBroker.addUserToGroup(userID, groupID, False)
          self.userBroker.session.commit()
    else:
      if not (groupUsers is None):
        if isinstance(groupUsers, types.StringTypes):
          self.userBroker.removeUserFromGroup(groupUsers, groupID)
        else:
          for userID in groupUsers:
            self.userBroker.removeUserFromGroup(userID, groupID, False)
          self.userBroker.session.commit()
    return self.groups(identifier=groupID)

# END GROUP HANDLING

# BEGIN OBJECT HANDLING

  @require(privileged())
  @cherrypy.expose
  def objects(self, identifier=None, obj=None,
              action=None, errorMsg=None):
    """
    renders the object page

    :param identifier: the identifier of the object to show the details
    :type identifier: Integer
    :param obj: A specific object to display in the group details
    :type obj: Object
    :param action: action which is taken (i.e. edit, insert, remove)
                   depending on the case the page is displayed differently
    :type action: String
    :param errorMsg: General error to be displayed
    :type errorMsg: String

    :Note: user either identifier or obj (the obj parameter has the priority)

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/objects.html')

    objects = self.objectBroker.getAll()
    errors = False
    if obj is None:
      if identifier is None:
        if (len(objects) > 0):
          obj = objects[0]
        else:
          obj = None
      else:
        obj = self.objectBroker.getByID(identifier)
    else:
      obj = obj
      # prevents unnecessary parameter
      errors = not obj.validate()

    remainingAttributes = self.objectBroker.getAttributesByObject(
                                                obj.identifier, False)
    attributes = obj.attributes
    return template.render(objects=objects, objectDetails=obj, errors=errors,
                           action=action,
                           remainingAttributes=remainingAttributes,
                           objectAttributes=attributes, errorMsg=errorMsg)

  @require(privileged())
  @cherrypy.expose
  def modifyObject(self, identifier=None, name=None, description=None,
                   action='insert'):
    """
    modifies or inserts an object with the data of the post

    :param identifier: The identifier of the object,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the object
    :type name: String
    :param description: The description of this object
    :type description: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    errorMsg = None
    obj = ObjectDefinition()
    if not action == 'insert':
      obj.identifier = identifier
    if not action == 'remove':
      obj.name = name
      obj.description = description
      try:
        if action == 'insert':
          self.objectBroker.insert(obj)
        if action == 'update':
          self.objectBroker.update(obj)
        action = None
      except ValidationException:
        self.getLogger().info('Object is invalid')
      except BrokerException as e:
        self.getLogger().info('An unexpected error occurred: {0}'.format(e))
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None
        obj = None
    else:
      try:
        self.objectBroker.removeByID(obj.identifier)
        obj = None
      except OperationException:
        errorMsg = 'Cannot delete this object. The object is still referenced.'

      action = None
    return self.objects(obj=obj, action=action, errorMsg=errorMsg)

  @require(privileged())
  @cherrypy.expose
  def editObjectAttribute(self, objID, operation, objectAttributes=None,
                          remainingAttributes=None):
    """
    modifies the relation between an object and its attributes

    :param groupID: The objID of the group
    :type groupID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingAttributes: The identifiers of the attributes which the object
                            is not attributed to
    :type remainingAttributes: Integer array
    :param objectAttributes: The identifiers of the attributes which the group is
                       attributed to
    :type objectAttributes: Integer array

    :returns: generated HTML
    """

    #Note remainingAttributes may be a string or an array!!!
    if operation == 'add':
      if not (remainingAttributes is None):
        if isinstance(remainingAttributes, types.StringTypes):
          self.objectBroker.addAttributeToObject(remainingAttributes, objID)
        else:
          for attribute in remainingAttributes:
            self.objectBroker.addAttributeToObject(attribute, objID, False)
          self.objectBroker.commit()
    else:
      #Note objectAttributes may be a string or an array!!!
      if not (objectAttributes is None):
        if isinstance(objectAttributes, types.StringTypes):
          self.objectBroker.removeAttributeFromObject(objectAttributes, objID)
        else:
          for attribute in objectAttributes:
            self.objectBroker.removeAttributeFromObject(attribute, objID)
          self.objectBroker.commit()
    return self.objects(identifier=objID)

# END OBJECT HANDLING

# BEGIN ATTRIBUTE HANDLING


  @require(privileged())
  @cherrypy.expose
  def attributes(self, identifier=None, attribute=None,
                 action=None, errorMsg=None):
    """
    renders the attribute page

    :param identifier: the identifier of the attribute to show the details
    :type identifier: Integer
    :param attribute: A specific attribute to display in the group details
    :type attribute: Attribute
    :param action: action which is taken (i.e. edit, insert, remove)
                   depending on the case the page is displayed differently
    :type action: String
    :param errorMsg: General error to be displayed
    :type errorMsg: String

    :Note: use either identifier or group (the group parameter has the priority)

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/attributes.html')

    attributes = self.attributeBroker.getAll()
    errors = False
    if attribute is None:
      if identifier is None:
        if (len(attributes) > 0):
          attribute = attributes[0]
        else:
          attribute = None
      else:
        attribute = self.attributeBroker.getByID(identifier)
    else:
      attribute = attribute
      errors = not attribute.validate()

    remainingAttributes = self.attributeBroker.getObjectsByAttribute(
                                              attribute.identifier, False)
    objects = attribute.objects
    return template.render(attributes=attributes, attributeDetails=attribute,
                           errors=errors, action=action,
                           cbValues=AttributeDefinition.getTableDefinitions(),
                           remainingObjects=remainingAttributes,
                           attributeObjects=objects,
                           errorMsg=errorMsg)


  @require(privileged())
  @cherrypy.expose
  def modifyAttribute(self, identifier=None, name=None, description='',
                      regex='^.*$', classIndex=0, action='insert'):
    """
    modifies or inserts an attribute with the data of the post

    :param identifier: The identifier of the attribute,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the attribute
    :type name: String
    :param description: The description of this attribute
    :type description: String
    :param regex: The regular expression to use to verify if the value is
                  correct
    :type regex: String
    :param classIndex: The index of the table to use for storing or getting the
                       attribute actual value
    :type classIndex: String
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    errorMsg = None
    attribute = AttributeDefinition()
    if not action == 'insert':
      attribute.identifier = identifier
    if not action == 'remove':
      attribute.name = name
      attribute.description = description
      attribute.classIndex = classIndex
      attribute.regex = regex

      try:
        if action == 'insert':
          self.attributeBroker.insert(attribute)
        if action == 'update':
          self.attributeBroker.update(attribute)
        action = None
      except ValidationException:
        self.getLogger().info('Attribute is invalid')
      except BrokerException as e:
        self.getLogger().info('An unexpected error occurred: {0}'.format(e))
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None
        attribute = None
    else:
      try:
        self.attributeBroker.removeByID(attribute.identifier)
        attribute = None
      except OperationException:
        errorMsg = ('Cannot delete this attribute.' +
                    ' The attribute is still referenced.')
      action = None

    return self.attributes(attribute=attribute, action=action,
                          errorMsg=errorMsg)


  @require(privileged())
  @cherrypy.expose
  def editAttributeObject(self, attrID, operation, attributeObjects=None,
                          remainingObjects=None):
    """
    modifies the relation between an attribute and its objects

    :param attrID: The attrID of the group
    :type attrID: Integer
    :param operation: the operation used in the context (either add or remove)
    :type operation: String
    :param remainingObjects: The identifiers of the objects which the attribute
                            is not attributed to
    :type remainingObjects: Integer array
    :param attributeObjects: The identifiers of the objects which the attribute is
                       attributed to
    :type attributeObjects: Integer array

    :returns: generated HTML

    """
    if operation == 'add':

      if not (remainingObjects is None):
        if isinstance(remainingObjects, types.StringTypes):
          self.attributeBroker.addObjectToAttribute(remainingObjects, attrID)
        else:
          for obj in remainingObjects:
            self.attributeBroker.addObjectToAttribute(obj, attrID, False)
          self.attributeBroker.session.commit()
    else:
      if not (attributeObjects is None):
        if isinstance(attributeObjects, types.StringTypes):
          self.groupBroker.removeObjectFromAttribute(attributeObjects, attrID)
        else:
          for obj in attributeObjects:
            self.attributeBroker.removeObjectFromAttribute(obj, attrID, False)
          self.attributeBroker.session.commit()
    return self.attributes(identifier=attrID)

# END ATTRIBUTE


