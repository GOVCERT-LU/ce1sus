# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 30, 2014
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def __is_viewable(event, user):
  """
  Checks if the page if viewable for the given group

  :param grous: A list of strings contrianing the group names
  :type groups: list

  :returns: Boolean
  """
  user_default_group = user.default_group
  # if the user has no default group he has no rights
  if user_default_group is None:
    return False
  # check if user is privileged
  result = user.privileged
  if not result:
    # check if the user created the event
    result = event.creator_group.identifier == user_default_group.identifier
  if not result:
    # the event has to be validated when the check before fail
    if not (event.bit_value.is_validated and event.bit_value.is_shareable and event.published):
      return False

  if not result:
    # check tlp level, this level is more priority
    result = event.tlp.identifier >= user_default_group.tlpLvl
    # check if the user belong to one of the common maingroups
    if not result:
        result = user_default_group in event.maingroups
    # check if the user belong to one of the common groups
    if not result:
      groups = user.default_group.subgroups
      for group in event.subgroups:
        if group in groups:
            return True
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
  if cache is None:
    result = __is_viewable(event, user)
  else:
    viewable = cache.get(event.identifier, None)
    if viewable == True:
      return True
    else:
      result = __is_viewable(event, user)
      cache[event.identifier] = result

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
