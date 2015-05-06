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


def is_object_viewable(instance, event_permissions, user_group, cache=None):
  if instance.properties.is_validated and instance.properties.is_shareable:
    return True
  elif event_permissions:
    # check if the user owns the attribtue
    if not instance.properties.is_validated:
      # if the user has the view non shared set then show
      if event_permissions.can_validate:
        return True
      else:
        # check if the user owns the obejct then return True
        return False
  if user_group:
    # check if tlp matches
    user_tlp = get_max_tlp(user_group)
    if instance.__class__.__name__ == 'ObservableComposition':
      return True
    elif instance.tlp_level_id >= user_tlp:
      return True

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
      if user.group_id == event.originating_group_id:
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
  result = is_object_viewable(event, user, user.group, cache)
  if not result:
    # check if the default group can download
    result = user.default_group.can_download
  return result


def get_max_tlp(user_group):
  if user_group.permissions.propagate_tlp:
    max_tlp = user_group.tlp_lvl
    for group in user_group.children:
      if group.tlp_lvl < max_tlp:
        max_tlp = group.tlp_lvl
      # check for group children
      child_max = get_max_tlp(group)
      if child_max < max_tlp:
        max_tlp = child_max
    return max_tlp
  else:
    return user_group.tlp_lvl
