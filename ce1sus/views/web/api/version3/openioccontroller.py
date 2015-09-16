# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 26, 2015
"""
from ce1sus.views.web.api.version3.base import AbstractRestController
from ce1sus.views.web.api.version3.handlers.adapters.openiocadapter import OpenIOCHandler


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class OpenIOCController(AbstractRestController):

  def set_instances(self, config):
    self.instances['0.1'] = OpenIOCHandler(config)
