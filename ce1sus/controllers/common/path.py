# -*- coding: utf-8 -*-

"""
(Description)

Created on 3 Sep 2015
"""

from ce1sus.common.utils import instance_code
from ce1sus.controllers.base import BaseController
from ce1sus.db.classes.internal.event import Event
from ce1sus.db.classes.internal.path import Path


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class PathController(BaseController):

  def __init__(self, config, session=None):
    super(PathController, self).__init__(config, session)



  def instance_to_path_recursive(self, instance):
    if isinstance(instance, Event):
      return '/{0}'.format(instance_code(instance)), instance
    else:
      path, event = self.instance_to_path_recursive(instance.parent)
      return '{0}/{1}'.format(path, instance_code(instance)), event

  def instance_to_path(self, instance, parent):
    if isinstance(instance, Event):
      return '/{0}'.format(instance_code(instance))
    else:
      if parent is None:
        parent = instance.parent
      if parent:
        parent_path = parent.path
        if parent.path:
          result = '{0}/{1}'.format(parent_path.path, instance_code(instance))
          return result
        else:
          raise ValueError('error {0} {1} has no path'.format(instance.parent.get_classname(), instance.parent.uuid))
      else:
        raise ValueError('error {0} {1} has no parent'.format(instance.get_classname(), instance.uuid))



  def make_path(self, instance, recursive=False, parent=None):
    if recursive:
      path, event = self.instance_to_path_recursive(instance)
    else:
      path = self.instance_to_path(instance, parent)

    path_instance = Path()

    path_instance.path = path

    if isinstance(instance, Event):
      path_instance.tlp_level_id = instance.tlp_level_id
      path_instance.dbcode = instance.dbcode
    else:
      if parent is None:
        parent = instance.parent

      path_instance.tlp_level_id = min(instance.tlp_level_id, parent.tlp_level_id)
      path_instance.dbcode = parent.dbcode & instance.dbcode

    if recursive:
      path_instance.event = event
    else:
      if isinstance(instance, Event):
        path_instance.event = None
      else:
        if parent is None:
          parent = instance.parent
        if isinstance(parent, Event):
          path_instance.event = parent
        else:
          path_instance.event = parent.path.root

    return path_instance
