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
