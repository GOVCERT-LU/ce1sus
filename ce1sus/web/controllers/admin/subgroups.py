# -*- coding: utf-8 -*-

"""
module handing the groups pages

Created: Nov 5, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.controllers.base import Ce1susBaseController
import cherrypy
from ce1sus.web.helpers.protection import require, privileged, requireReferer
from dagr.db.broker import IntegrityException, BrokerException, \
  ValidationException, NothingFoundException
import types as types
from ce1sus.brokers.staticbroker import TLPLevel
from ce1sus.brokers.permission.subgroupbroker import SubGroupBroker


class SubGroupController(Ce1susBaseController):

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.subgroupBroker = self.brokerFactory(SubGroupBroker)

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the group page

    :returns: generated HTML
    """

    template = self.getTemplate('/admin/subgroups/subgroupBase.html')
    return self.cleanHTMLCode(template.render())

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def leftContent(self):
    """
    renders the left content of the group index page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/subgroups/subgroupLeft.html')
    groups = self.subgroupBroker.getAll()
    return self.cleanHTMLCode(template.render(groups=groups))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def rightContent(self, subGroupid=0, group=None):
    """
    renders the right content of the group index page

    :param subGroupid: The group id of the desired displayed group
    :type subGroupid: Integer
    :param group: Similar to the previous attribute but prevents
                      additional loadings
    :type group: Group

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/subgroups/subgroupRight.html')
    if group is None:
      try:
        group = self.subgroupBroker.getByID(subGroupid)
      except NothingFoundException:
        group = None
    else:
      group = group
    remGroups = None
    groups = None
    if not group is None:
      remGroups = self.subgroupBroker.getGroupsBySubGroup(group.identifier,
                                                             False)
      groups = group.groups
    return self.cleanHTMLCode(template.render(subgroupDetails=group,
                           remainingGroups=remGroups,
                           groups=groups,
                           cbTLPValues=TLPLevel.getDefinitions()))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def addSubGroup(self):
    """
    renders the add a group page

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/subgroups/subgroupModal.html')
    return self.cleanHTMLCode(template.render(group=None, errorMsg=None,
                           cbTLPValues=TLPLevel.getDefinitions()))

  # pylint: disable=R0913
  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def modifySubGroup(self, identifier=None, name=None,
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
    template = self.getTemplate('/admin/groups/groupModal.html')
    group = self.subgroupBroker.buildSubGroup(identifier,
                                        name,
                                        description,
                                        action)
    try:
      if action == 'insert':
        self.subgroupBroker.insert(group)
      if action == 'update':
        self.subgroupBroker.update(group)
      if action == 'remove':
        self.subgroupBroker.removeByID(group.identifier)
      return self.returnAjaxOK()
    except IntegrityException as e:
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
  def editSubGroup(self, groupid):
    """
    renders the edit group page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer

    :returns: generated HTML
    """
    template = self.getTemplate('/admin/subgroups/subgroupModal.html')
    errorMsg = None
    try:
      group = self.subgroupBroker.getByID(groupid)
    except BrokerException as e:
      self.getLogger().error('An unexpected error occurred: {0}'.format(e))
      errorMsg = 'An unexpected error occurred: {0}'.format(e)
    return self.cleanHTMLCode(template.render(group=group, errorMsg=errorMsg,
                           cbTLPValues=TLPLevel.getDefinitions()))

  @require(privileged(), requireReferer(('/internal')))
  @cherrypy.expose
  def editSubGroupGroup(self, subGroupID, operation,
                     subGroupGroups=None, remainingGroups=None):
    """
    modifies the relation between a group and its users

    :param subGroupID: The subGroupID of the group
    :type subGroupID: Integer
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
        if not (remainingGroups is None):
          if isinstance(remainingGroups, types.StringTypes):
            self.subgroupBroker.addGroupToSubGroup(remainingGroups,
                                                   subGroupID)
          else:
            for groupID in remainingGroups:
              self.subgroupBroker.addGroupToSubGroup(groupID,
                                                     subGroupID,
                                                     False)
            self.subgroupBroker.doCommit(True)
      else:
        if not (subGroupGroups is None):
          if isinstance(subGroupGroups, types.StringTypes):
            self.subgroupBroker.removeSubGroupFromGroup(subGroupGroups,
                                                        subGroupID)
          else:
            for groupID in subGroupGroups:
              self.subgroupBroker.removeSubGroupFromGroup(groupID,
                                                       subGroupID,
                                                       False)
            self.subgroupBroker.doCommit(True)
      return self.returnAjaxOK()
    except BrokerException as e:
      return "Error {0}".format(e)
