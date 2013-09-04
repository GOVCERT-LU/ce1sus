# -*- coding: utf-8 -*-

"""
module handing the attributes pages

Created: Aug 26, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.web.controllers.base import BaseController
import cherrypy
from ce1sus.brokers.permissionbroker import UserBroker, GroupBroker, User
from ce1sus.web.helpers.protection import require, privileged, requireReferer
from dagr.web.helpers.pagination import Paginator
from dagr.helpers.ldaphandling import LDAPHandler, LDAPException
from dagr.db.broker import OperationException, BrokerException, \
  ValidationException
import types as types

class DeletionException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class UserController(BaseController):
  """Controller handling all the requests for users"""

  def __init__(self):
    BaseController.__init__(self)
    self.userBroker = self.brokerFactory(UserBroker)
    self.groupBroker = self.brokerFactory(GroupBroker)

  @require(privileged())
  @cherrypy.expose
  def index(self):
    """
    renders the user page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/users/userBase.html')
    return template.render()

  @require(privileged())
  @cherrypy.expose
  def leftContent(self):
    """
    renders the left content of the user index page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/users/userLeft.html')
    users = self.userBroker.getAll()
    return template.render(users=users)

  @require(privileged())
  @cherrypy.expose
  def rightContent(self, userid=0, user=None):
    """
    renders the right content of the user index page

    :param userid: The user id of the desired displayed user
    :type userid: Integer
    :param user: Similar to the previous attribute but prevents
                      additional loadings
    :type user: User

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/users/userRight.html')
    if user is None:
      if userid is None or userid == 0:
        user = None
      else:
        user = self.userBroker.getByID(userid)
    else:
      user = user
      # prevents unnecessary parameter
    remainingGroups = None
    groups = None
    if not user is None:
      remainingGroups = self.userBroker.getGroupsByUser(user.identifier, False)
      groups = user.groups
    return template.render(userDetails=user,
                           userGroups=groups,
                           remainingGroups=remainingGroups)


  @require(privileged())
  @cherrypy.expose
  def addUser(self):
    """
    renders the add a user page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/users/userModal.html')
    return template.render(user=None, errorMsg=None)

  @require(privileged())
  @cherrypy.expose
  def ldapUsersTable(self):
    """
    renders the table with the ldap users

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/users/ldapUserTable.html')
    labels = [{'radio':'#'},
              {'uid':'username'},
              {'mail':'Email'},
              {'displayName':'Name'}
              ]

    lh = LDAPHandler.getInstance()
    lh.open()
    ldapPaginator = Paginator(items=lh.getAllUsers(),
                          labelsAndProperty=labels)
    lh.close()
    return template.render(ldapPaginator=ldapPaginator, errorMsg=None)

  @require(privileged())
  @cherrypy.expose
  def modifyUser(self, identifier=None, username=None, password=None,
                 priv=None, email=None, action='insert',
                 ldapUsersTable_length=None):
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
    :param priv: Is the user privileged to access the administration section
    :type priv: Integer
    :param action: action which is taken (i.e. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/users/userModal.html')
    del ldapUsersTable_length
    errorMsg = None
    user = User()
    if not action == 'insert':
      user.identifier = identifier
    if not action == 'remove':
      user.email = email
      user.password = password
      user.username = username
      user.privileged = priv
      if action == 'insertLDAP':
        user.identifier = None
        # get LDAP user
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
      try:
        if action == 'insert' or action == 'insertLDAP':
          self.userBroker.insert(user)
        if action == 'update':
          self.userBroker.update(user)
        action = None
      except ValidationException:
        self.getLogger().info('User is invalid')
      except BrokerException as e:
        self.getLogger().error('An unexpected error occurred: {0}'.format(e))
        errorMsg = 'An unexpected error occurred: {0}'.format(e)
        action = None
    else:
      try:
        if (user.identifier == '1'):
          raise DeletionException('First user cannot be removed.')
        self.userBroker.removeByID(user.identifier)
      except OperationException:
        errorMsg = ('Cannot delete user. The user is referenced by elements.'
                    + ' Remove his groups instead.')
      except DeletionException as e:
        return e
      action = None
    if action == None:
      # ok everything went right
      return self.returnAjaxOK()
    else:
      return template.render(user=user, errorMsg=errorMsg)

  @require(privileged())
  @cherrypy.expose
  def editUser(self, userid):
    """
    renders the edit a user page

    :param userid: The user id of the desired displayed user
    :type userid: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/users/userModal.html')
    errorMsg = None
    try:
      user = self.userBroker.getByID(userid)
    except BrokerException as e:
      self.getLogger().error('An unexpected error occurred: {0}'.format(e))
      errorMsg = 'An unexpected error occurred: {0}'.format(e)
    return template.render(user=user, errorMsg=errorMsg)

  @require(privileged(), requireReferer('/admin', ('/internal')))
  @cherrypy.expose
  def editUserGroups(self, userID, operation, remainingGroups=None,
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
    try:
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
      return self.returnAjaxOK()
    except BrokerException as e:
      return e
