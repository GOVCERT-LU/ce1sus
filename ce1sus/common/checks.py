# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def is_user_priviledged(user):
  return user.permissions.privileged


def is_object_viewable(instance, event_permissions, cache=None):
  if instance.properties.is_validated and instance.properties.is_shareable:
    return True
  elif event_permissions:
    if event_permissions.can_validate:
      return True
    else:
      return False
  else:
    return False


def is_event_owner(event, user):
  """
  Returns true if the event is created by the user

  :param event:
  :type event: Event
  :param user:
  :type user: User

  :returns: Boolean
  """
  if event and user:
    if is_user_priviledged(user):
      return True
    else:
      if user.group_id == event.creator_group_id:
        return True
      else:
        return False
  else:
    return False


def get_view_message(result, event_id, username, permission):
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
    return 'User "{1}" can perform action "{2}" on event "{0}"'.format(event_id, username, permission)
  else:
    return 'User "{1}" is not allowed perform action "{2}" on event "{0}"'.format(event_id, username, permission)


def get_item_view_message(result, event_id, item_id, username, permission):
  if result:
    return 'User "{1}" can perform action "{2}" on event "{0}" for item {3}'.format(event_id, username, permission, item_id)
  else:
    return 'User "{1}" is not allowed perform action "{2}" on event "{0}" for item {3}'.format(event_id, username, permission, item_id)


def can_user_download(event, user, cache=None):
  """
  Returns true if the user can download from the event

  :param event:
  :type event: Event
  :param user:
  :type user: User

  :returns: Boolean
  """
  # TODO: rethink this
  result = is_object_viewable(event, user, cache)
  if not result:
    # check if the default group can download
    result = user.default_group.can_download
  return result
