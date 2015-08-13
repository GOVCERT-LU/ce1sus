# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""
from ce1sus.controllers.common.updater.base import BaseUpdater


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class CyboxUpdater(BaseUpdater):

  def update_observable(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version
