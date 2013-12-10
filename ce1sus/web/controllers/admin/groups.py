# -*- coding: utf-8 -*-

"""
module handing the groups pages

Created: Aug 19, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, privileged, requireReferer
from dagr.db.broker import OperationException, BrokerException, \
  ValidationException, NothingFoundException
import types as types
from ce1sus.brokers.staticbroker import TLPLevel
from ce1sus.brokers.permission.groupbroker import GroupBroker


class GroupController(Ce1susBaseController):
  """Controller handling all the requests for groups"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.groupBroker = self.brokerFactory(GroupBroker)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the group page

    :returns: generated HTML
    """

    template = self.getTemplate('/admin/groups/groupBase.html')
    return self.cleanHTMLCode(template.render())

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def leftContent(self):
    """
    renders the left content of the group index page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/groups/groupLeft.html')
    groups = self.groupBroker.getAll()
    return self.cleanHTMLCode(template.render(groups=groups))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def rightContent(self, groupid=0, group=None):
    """
    renders the right content of the group index page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer
    :param group: Similar to the previous attribute but prevents
                      additional loadings
    :type group: Group

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/groups/groupRight.html')
    if group is None:
      try:
        group = self.groupBroker.getByID(groupid)
      except NothingFoundException:
        group = None
    else:
      group = group
    remSubGroups = None
    subgroups = None
    if not group is None:
      remSubGroups = self.groupBroker.getSubGroupsByGroup(group.identifier,
                                                          False)
      subgroups = group.subgroups
    return self.cleanHTMLCode(template.render(groupDetails=group,
                           remainingSubGroups=remSubGroups,
                           subgroups=subgroups,
                           cbTLPValues=TLPLevel.getDefinitions()))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def addGroup(self):
    """
    renders the add a group page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/groups/groupModal.html')
    return self.cleanHTMLCode(template.render(group=None, errorMsg=None,
                           cbTLPValues=TLPLevel.getDefinitions()))

  # pylint: disable=R0913
  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def modifyGroup(self, identifier=None, name=None,
                  description=None, download=None, action='insert',
                  tlpLvl=None, email=None, usermails=None):
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
    template = self.getTemplate('/admin/groups/groupModal.html')
    group = self.groupBroker.buildGroup(identifier,
                                        name,
                                        description,
                                        download,
                                        action,
                                        tlpLvl,
                                        email,
                                        usermails)
    try:
      if action == 'insert':
        self.groupBroker.insert(group)
      if action == 'update':
        self.groupBroker.update(group)
      if action == 'remove':
        identifier = group.identifier
        if identifier == '1' or identifier == 1:
          return 'Cannot delete this group. The group is essential to the application.'
        self.groupBroker.removeByID(group.identifier)
      return self.returnAjaxOK()
    except OperationException as e:
      self.getLogger().info('OperationError occurred: {0}'.format(e))
      return 'Cannot delete this group. The group is still referenced.'
    except ValidationException:
      self.getLogger().debug('Group is invalid')
      return self.returnAjaxPostError() + self.cleanHTMLCode(template.render(group=group,
                           cbTLPValues=TLPLevel.getDefinitions()))
    except BrokerException as e:
      self.getLogger().error('An unexpected error occurred: {0}'.format(e))
      return "Error {0}".format(e)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def editGroup(self, groupid):
    """
    renders the edit group page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/groups/groupModal.html')
    errorMsg = None
    try:
      group = self.groupBroker.getByID(groupid)
    except BrokerException as e:
      self.getLogger().error('An unexpected error occurred: {0}'.format(e))
      errorMsg = 'An unexpected error occurred: {0}'.format(e)
    return self.cleanHTMLCode(template.render(group=group, errorMsg=errorMsg,
                           cbTLPValues=TLPLevel.getDefinitions()))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def editGroupSubGroup(self, groupID, operation,
                     groupSubGroups=None, remainingSubGroups=None):
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
    try:
      if operation == 'add':
        if not (remainingSubGroups is None):
          if isinstance(remainingSubGroups, types.StringTypes):
            self.groupBroker.addSubGroupToGroup(remainingSubGroups, groupID)
          else:
            for subGroupID in remainingSubGroups:
              self.groupBroker.addSubGroupToGroup(subGroupID, groupID, False)
            self.groupBroker.doCommit(True)
      else:
        if not (groupSubGroups is None):
          if isinstance(groupSubGroups, types.StringTypes):
            self.groupBroker.removeSubGroupFromGroup(groupSubGroups, groupID)
          else:
            for subGroupID in groupSubGroups:
              self.groupBroker.removeSubGroupFromGroup(subGroupID,
                                                       groupID,
                                                       False)
            self.groupBroker.doCommit(True)
      return self.returnAjaxOK()
    except BrokerException as e:
      return "Error {0}".format(e)
