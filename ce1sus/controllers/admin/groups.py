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
from ce1sus.web.helpers.protection import require, privileged, require_referer
from dagr.db.broker import IntegrityException, BrokerException, \
  ValidationException, NothingFoundException
import types as types
from ce1sus.brokers.staticbroker import TLPLevel
from ce1sus.brokers.permission.groupbroker import GroupBroker


class GroupController(Ce1susBaseController):
  """Controller handling all the requests for groups"""

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.group_broker = self.broker_factory(GroupBroker)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the group page

    :returns: generated HTML
    """

    template = self._get_template('/admin/groups/groupBase.html')
    return self.clean_html_code(template.render())

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def left_content(self):
    """
    renders the left content of the group index page

    :returns: generated HTML
    """
    template = self._get_template('/admin/groups/groupLeft.html')
    groups = self.group_broker.get_all()
    return self.clean_html_code(template.render(groups=groups))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def right_content(self, groupid=0, group=None):
    """
    renders the right content of the group index page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer
    :param group: Similar to the previous attribute but prevents
                      additional loadings
    :type group: Group

    :returns: generated HTML
    """
    template = self._get_template('/admin/groups/groupRight.html')
    if group is None:
      try:
        group = self.group_broker.get_by_id(groupid)
      except NothingFoundException:
        group = None
    else:
      group = group
    rem_subgroups = None
    subgroups = None
    if not group is None:
      rem_subgroups = self.group_broker.get_subgroups_by_group(group.identifier,
                                                          False)
      subgroups = group.subgroups
    return self.clean_html_code(template.render(groupDetails=group,
                           remainingSubGroups=rem_subgroups,
                           subgroups=subgroups,
                           cbTLPValues=TLPLevel.get_definitions()))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def add_group(self):
    """
    renders the add a group page

    :returns: generated HTML
    """
    template = self._get_template('/admin/groups/groupModal.html')
    return self.clean_html_code(template.render(group=None, errorMsg=None,
                           cbTLPValues=TLPLevel.get_definitions()))

  # pylint: disable=R0913
  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def modify_group(self, identifier=None, name=None,
                  description=None, download=None, action='insert',
                  tlp_lvl=None, email=None, usermails=None):
    """
    modifies or inserts a group with the data of the post

    :param identifier: The identifier of the group,
                       is only used in case the action is edit or remove
    :type identifier: Integer
    :param name: The name of the group
    :type name: String
    :param description: The description of this group
    :type description: String
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self._get_template('/admin/groups/groupModal.html')
    group = self.group_broker.build_group(identifier,
                                        name,
                                        description,
                                        download,
                                        action,
                                        tlp_lvl,
                                        email,
                                        usermails)
    try:
      if action == 'insert':
        self.group_broker.insert(group)
      if action == 'update':
        self.group_broker.update(group)
      if action == 'remove':
        identifier = group.identifier
        if identifier == '1' or identifier == 1:
          return ('Cannot delete this group. The group is essential to '
                  + 'the application.')
        self.group_broker.remove_by_id(group.identifier)
      return self._return_ajax_ok()
    except IntegrityException as error:
      error_msg = '{0}'.format(error)
      self._get_logger().info('OperationError occurred: {0}'.format(error))
      if 'FK_User_Group_Group_id' in error_msg:
        return ('Cannot delete this group. The group is still referenced '
                + 'by some Users.')
      elif 'FK_Events_Groups_creatorGroup_groupID' in error_msg:
        return ('Cannot delete this group. The group is still referenced as '
                + 'creator Group by some Events.')
      else:
        return 'Cannot delete this group. The group is still referenced.'
    except ValidationException:
      self._get_logger().debug('Group is invalid')
      return (self._return_ajax_post_error()
              + self.clean_html_code(template.render(group=group,
                           cbTLPValues=TLPLevel.get_definitions())))
    except BrokerException as error:
      self._get_logger().error('An unexpected error occurred: {0}'.format(error))
      return "Error {0}".format(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_group(self, groupid):
    """
    renders the edit group page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer

    :returns: generated HTML
    """
    template = self._get_template('/admin/groups/groupModal.html')
    error_msg = None
    try:
      group = self.group_broker.get_by_id(groupid)
    except BrokerException as error:
      self._get_logger().error('An unexpected error occurred: {0}'.format(error))
      error_msg = 'An unexpected error occurred: {0}'.format(error)
    return self.clean_html_code(template.render(group=group, error_msg=error_msg,
                           cbTLPValues=TLPLevel.get_definitions()))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_group_subgroup(self, group_id, operation,
                     group_subgroups=None, remaining_subgroups=None):
    """
    modifies the relation between a group and its users

    :param group_id: The group_id of the group
    :type group_id: Integer
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
        if not (remaining_subgroups is None):
          if isinstance(remaining_subgroups, types.StringTypes):
            self.group_broker.add_subgroup_to_group(remaining_subgroups, group_id)
          else:
            for subgroup_id in remaining_subgroups:
              self.group_broker.add_subgroup_to_group(subgroup_id, group_id, False)
            self.group_broker.do_commit(True)
      else:
        if not (group_subgroups is None):
          if isinstance(group_subgroups, types.StringTypes):
            self.group_broker.remove_subgroup_from_group(group_subgroups, group_id)
          else:
            for subgroup_id in group_subgroups:
              self.group_broker.remove_subgroup_from_group(subgroup_id,
                                                       group_id,
                                                       False)
            self.group_broker.do_commit(True)
      return self._return_ajax_ok()
    except BrokerException as error:
      return "Error {0}".format(error)
