# -*- coding: utf-8 -*-

"""
(Description)

Created on Sep 2, 2015
"""
from ce1sus.db.classes.internal.common import TLP


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

def get_max_tlp(group):
  if group:
    if group.permissions.propagate_tlp:
      max_tlp = group.tlp_lvl
      for group in group.children:
        if group.tlp_lvl < max_tlp:
          max_tlp = group.tlp_lvl
        # check for group children
        child_max = get_max_tlp(group)
        if child_max < max_tlp:
          max_tlp = child_max
      return max_tlp
    else:
      return group.tlp_lvl
  else:
    return TLP.get_by_value('White')

def can_user_download(event, user):
  """
  Returns true if the user can download from the event

  :param event:
  :type event: Event
  :param user:
  :type user: User

  :returns: Boolean
  """
  if user.permissions.privileged:
    return True
  if user.group:
    result = user.group.permissions.can_download
    return result
  else:
    return False

ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'

def baseencode(number):
    base = ''
    while number != 0:
        number, i = divmod(number, len(ALPHABET))
        base = ALPHABET[i] + base
    return base

def basedecode(number):
    return int(number, len(ALPHABET))

def instance_code(instance):
  result = table_code(instance.get_table_name())
  result = '{0}-{1}'.format(result, instance.uuid)
  return result

def table_code(value):
  result = 0
  for c in value:
    result = result + ord(c)
  return baseencode(result)