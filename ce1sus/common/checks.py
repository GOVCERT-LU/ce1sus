# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""
from ce1sus.db.classes.group import EventPermissions

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def is_user_priviledged(user):

  return user.permissions.privileged


def is_event_owner(event, user):
  """
  Returns true if the event is created by the user

  :param event:
  :type event: Event
  :param user:
  :type user: User

  :returns: Boolean
  """
  if is_user_priviledged(user):
    return True
  else:
    if user.group_id == event.creator_group_id:
      return True
    else:
      return False


def get_event_permissions(event, user):
  """
  Checks if the page if viewable for the given group

  :returns: Boolean in case no access or full access and an EventPermission in case the user is limited
  """
  # if the user has no default group he has no rights
  if user.group_id is None:
    return False

  # check if user is privileged or the event owner
  result = is_event_owner(event, user)

  if not result:
    # the event has to be validated and shared to view it
    if not (event.properties.is_validated and event.properties.is_shareable):
      return False

  if not result:
    # if the event is still not visible the event has to have a lower or equal tlp level
    user_tlp = user.group.tlp_lvl
    result = event.tlp.identifier >= user_tlp

    # check if the user belong to one of the event groups
    if not result:
      for group in event.groups:
        # first check if the user is in agroup which has been specified
        if group.group.identifier == user.group_id:
          # check if the user can see it
          return group.group.permissions
  if result:
    return result
  else:
    raise Exception(u'Unknown error occurred during event checks')


def get_view_message(result, event_id, username):
  """
  Returns the message for loggin

  :param event_id: identifer of the event
  :type event_id: Integer
  :param username:
  :type username: String
  :param result:
  :type result: Boolean
  """
  if result:
    return 'Event "{0}" is viewable for user "{1}"'.format(event_id, username)
  else:
    return 'Event "{0}" is not viewable for user "{1}"'.format(event_id, username)


def is_viewable(event, user, cache=None):
  """
  Checks if the page if viewable for the given user

  :param event:
  :type event: Event
  :param user:
  :type user: User
  :param cache:
  :type cache: Dictionary

  :returns: Boolean
  """
  result = None
  if event:
    # check if cache
    if cache:
      permissions = cache.get(event.identifier, None)
      # if None the event is not available inside the cache
      if permissions:
        if isinstance(permissions, EventPermissions):
          result = permissions.can_view
        else:
          result = permissions

    if not result:
      # either there was no cache or the event was not inside the cache perform checks
      permissions = get_event_permissions(event, user)
      if isinstance(permissions, EventPermissions):
        result = permissions.can_view
      else:
        result = permissions
      # put result in the cache if there is one
      cache[event.identifier] = result
      # perform checks
  else:
    result = False

  # if the result is still not set throw an error
  if result:
    return result
  else:
    raise Exception(u'Unknown error occurred during event checks')
