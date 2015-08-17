# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 10, 2015
"""
from ce1sus.test.common.base import BaseTest


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class LoggedInBase(BaseTest):
  
  def setUp(self):
    super(LoggedInBase, self).setUp()
    self.apiKey = '4a5e3a7e8aa200cbde64432df11c4b459b154499'
    self.post('/login')



  def tearDown(self):
    self.get('/logout')
    super(LoggedInBase, self).tearDown()

