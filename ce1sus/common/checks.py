# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def is_viewable(event, user_default_group, user_priv=False):
  """
  Checks if the page if viewable for the given group

  :param grous: A list of strings contrianing the group names
  :type groups: list

  :returns: Boolean
  """
  # if the user has no default group he has no rights
  if user_default_group is None:
    return False
  # check if user is privileged
  result = user_priv
  if not result:
    # check if the user created the event
    result = event.creator_group.identifier == user_default_group.identifier
  if not result:
    # the event has to be validated when the check before fail
    if not (event.bit_value.is_validated and event.bit_value.is_shareable and event.published):
      return False

  if not result:
    user_tlp = user_default_group.tlp_lvl
    # check tlp level, this level is more priority
    result = event.tlp.identifier >= user_tlp
    # check if the user belong to one of the common maingroups
    if not result:
      for group in event.maingroups:
        if group.identifier == user_default_group.identifier:
          result = True
          break
    # check if the user belong to one of the common groups
    if not result:
      for usr_subgroup in user_default_group.subgroups:
        for subgroup in event.subgroups:
          if usr_subgroup.identifier == subgroup.identifier:
              result = True
              break
  return result


def check_viewable_message(result, event_id, username):
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


def check_if_event_is_viewable(event, user, cache=None):
  """
  Checks if the page if viewable for the given group

  :param event:
  :type event: Event
  :param user:
  :type user: User
  :param cache:
  :type cache: Dictionary

  :returns: Boolean
  """
  # get eventfrom session
  if event:
    if cache is None:
      result = is_viewable(event, user.default_group, user.privileged == 1)
    else:
      viewable = cache.get(event.identifier, None)
      if viewable is True:
        return True
      else:
        result = is_viewable(event, user.default_group, user.privileged == 1)
        cache[event.identifier] = result
  else:
    return False
  return result


def is_event_owner(event, user):
  """
  Returns true if the event is created by the user

  :param event:
  :type event: Event
  :param user:
  :type user: User

  :returns: Boolean
  """
  if user.privileged == 1:
    return True
  else:
    if user.group_id == event.creator_group_id:
      return True
    else:
      return False


def can_user_download(event, user, cache=None):
  """
  Returns true if the user can download from the event

  :param event:
  :type event: Event
  :param user:
  :type user: User

  :returns: Boolean
  """
  result = check_if_event_is_viewable(event, user, cache)
  if not result:
    # check if the default group can download
    result = user.default_group.can_download
  return result
