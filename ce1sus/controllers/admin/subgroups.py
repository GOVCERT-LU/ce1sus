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
from ce1sus.web.helpers.protection import require, privileged, require_referer
from dagr.db.broker import IntegrityException, BrokerException, \
  ValidationException, NothingFoundException
import types as types
from ce1sus.brokers.staticbroker import TLPLevel
from ce1sus.brokers.permission.subgroupbroker import SubGroupBroker


class SubGroupController(Ce1susBaseController):

  def __init__(self):
    Ce1susBaseController.__init__(self)
    self.subgroup_broker = self.broker_factory(SubGroupBroker)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def index(self):
    """
    renders the group page

    :returns: generated HTML
    """

    template = self._get_template('/admin/subgroups/subgroupBase.html')
    return self.clean_html_code(template.render())

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def left_content(self):
    """
    renders the left content of the group index page

    :returns: generated HTML
    """
    template = self._get_template('/admin/subgroups/subgroupLeft.html')
    groups = self.subgroup_broker.get_all()
    return self.clean_html_code(template.render(groups=groups))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def right_content(self, subgroupid=0, group=None):
    """
    renders the right content of the group index page

    :param subgroupid: The group id of the desired displayed group
    :type subgroupid: Integer
    :param group: Similar to the previous attribute but prevents
                      additional loadings
    :type group: Group

    :returns: generated HTML
    """
    template = self._get_template('/admin/subgroups/subgroupRight.html')
    if group is None:
      try:
        group = self.subgroup_broker.get_by_id(subgroupid)
      except NothingFoundException:
        group = None
    else:
      group = group
    rem_groups = None
    groups = None
    if not group is None:
      rem_groups = self.subgroup_broker.get_groups_by_subgroup(group.identifier,
                                                             False)
      groups = group.maingroups
    return self.clean_html_code(template.render(subgroupDetails=group,
                           remainingGroups=rem_groups,
                           groups=groups,
                           cbTLPValues=TLPLevel.get_definitions()))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def add_subgroup(self):
    """
    renders the add a group page

    :returns: generated HTML
    """
    template = self._get_template('/admin/subgroups/subgroupModal.html')
    return self.clean_html_code(template.render(group=None, errorMsg=None,
                           cbTLPValues=TLPLevel.get_definitions()))

  # pylint: disable=R0913
  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def modify_subgroup(self, identifier=None, name=None,
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
    :param action: action which is taken (i.error. edit, insert, remove)
    :type action: String

    :returns: generated HTML
    """
    template = self._get_template('/admin/groups/groupModal.html')
    group = self.subgroup_broker.build_subgroup(identifier,
                                        name,
                                        description,
                                        action)
    try:
      if action == 'insert':
        self.subgroup_broker.insert(group)
      if action == 'update':
        self.subgroup_broker.update(group)
      if action == 'remove':
        self.subgroup_broker.remove_by_id(group.identifier)
      return self._return_ajax_ok()
    except IntegrityException as error:
      self._get_logger().info('OperationError occurred: {0}'.format(error))
      return 'Cannot delete this group. The group is still referenced.'
    except ValidationException:
      self._get_logger().debug('Group is invalid')
      return self._return_ajax_post_error() + self.clean_html_code(
                                                        template.render(
                                                        group=group,
                           cbTLPValues=TLPLevel.get_definitions()))
    except BrokerException as error:
      self._get_logger().error('An unexpected error occurred: {0}'.format(error))
      return "Error {0}".format(error)

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_subgroup(self, groupid):
    """
    renders the edit group page

    :param groupid: The group id of the desired displayed group
    :type groupid: Integer

    :returns: generated HTML
    """
    template = self._get_template('/admin/subgroups/subgroupModal.html')
    error_msg = None
    try:
      group = self.subgroup_broker.get_by_id(groupid)
    except BrokerException as error:
      self._get_logger().error('An unexpected error occurred: {0}'.format(error))
      error_msg = 'An unexpected error occurred: {0}'.format(error)
    return self.clean_html_code(template.render(group=group, error_msg=error_msg,
                           cbTLPValues=TLPLevel.get_definitions()))

  @require(privileged(), require_referer(('/internal')))
  @cherrypy.expose
  def edit_subgroup_group(self, subgroup_id, operation,
                     subgroup_groups=None, remaining_groups=None):
    """
    modifies the relation between a group and its users

    :param subgroup_id: The subgroup_id of the group
    :type subgroup_id: Integer
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
        if not (remaining_groups is None):
          if isinstance(remaining_groups, types.StringTypes):
            self.subgroup_broker.add_group_to_subgroup(remaining_groups,
                                                   subgroup_id)
          else:
            for group_id in remaining_groups:
              self.subgroup_broker.add_group_to_subgroup(group_id,
                                                     subgroup_id,
                                                     False)
            self.subgroup_broker.do_commit(True)
      else:
        if not (subgroup_groups is None):
          if isinstance(subgroup_groups, types.StringTypes):
            self.subgroup_broker.remove_subgroup_from_group(subgroup_groups,
                                                        subgroup_id)
          else:
            for group_id in subgroup_groups:
              self.subgroup_broker.remove_subgroup_from_group(group_id,
                                                       subgroup_id,
                                                       False)
            self.subgroup_broker.do_commit(True)
      return self._return_ajax_ok()
    except BrokerException as error:
      return "Error {0}".format(error)
