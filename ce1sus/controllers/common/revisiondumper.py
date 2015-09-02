# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 17, 2015
"""
import json
from os import makedirs
from os.path import exists
import time

from ce1sus.common.classes.cacheobject import CacheObject
from ce1sus.controllers.base import BaseController
from ce1sus.db.classes.internal.usrmgt.user import User


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class RevisionDumper(BaseController):

  def __init__(self, config, session=None):
    super(RevisionDumper, self).__init__(config, session)
    self.config = config
    self.destination = self.config.get('ce1sus', 'revdir', None)
    if self.destination:
      if not exists(self.destination):
          makedirs(self.destination)

  def save_old_copy(self, old_instance):
    if self.destination:
      version = ''
      if hasattr(old_instance, 'version'):
        version = '{0}_'.format(old_instance.version.version)
      timestr = time.strftime("%Y%m%d-%H%M%S")
      filename = '{0}-{1}_{2}{3}.json'.format(old_instance.get_classname(), old_instance.uuid, version, timestr)

      cache_object = CacheObject()
      cache_object.user = User()
      cache_object.user.permissions.privileged = True
      cache_object.inflated = True
      cache_object.complete = True

      f = open('{0}/{1}'.format(self.destination, filename), 'w+')
      f.write(json.dumps(old_instance.to_dict(cache_object), indent=4, sort_keys=True))
      f.close()
