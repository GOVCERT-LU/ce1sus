# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 10, 2015
"""
from datetime import datetime

from ce1sus.controllers.admin.user import UserController
from ce1sus.db.classes.internal.usrmgt.user import User
from ce1sus.helpers.common.hash import hashSHA1
from ce1sus.test.common.base import BaseTest, HTTPError


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class TestLogin(BaseTest):

  def setUp(self):
    BaseTest.setUp(self)
    self.user_controller = self.controller_factory(UserController)

  def tearDown(self):
    BaseTest.tearDown(self)

  def testloginlogoutAPIKEY(self):
    try:
      self.apiKey = '4a5e3a7e8aa200cbde64432df11c4b459b154499'
      text = self.post('/login')
      if text:
        assert True

        text = self.get('/logout')
        if text:
          assert True
        else:
          assert False
      else:
        assert False
    except HTTPError as error:
      if error.code == 403:
        assert False
      else:
        assert False

  def testloginlogout(self):
    try:
      self.apiKey = ''

      text = self.post('/login', data={'usr':'admin', 'pwd':'admin'})
      if text:
        assert True

        text = self.get('/logout')
        if text:
          assert True
        else:
          assert False
      else:
        assert False
    except HTTPError as error:
      if error.code == 403:
        assert False
      else:
        assert False


  def testloginFailName(self):
    try:
      self.apiKey = ''
      text = self.post('/login', data={'usr':'admin2', 'pwd':'admin'})
      if text:
        assert False
      else:
        assert True
    except HTTPError as error:
      if error.code == 401:
        assert True
      else:
        assert False

  def testloginDisabled(self):
    try:
      salt = self.config.get('ce1sus', 'salt')
      user = User()
      user.name = 'Root Disabled'
      user.sirname = 'Administrator Disabled'
      user.username = 'admindisabled'
      user.password = hashSHA1('admin' + salt)
      user.last_login = None
      user.email = 'admin2@example.com'
      user.api_key = None
      user.gpg_key = None
      user.activated = datetime.now()
      user.dbcode = 31
      user.permissions.disabled = True
      user.activation_sent = None
      user.activation_str = 'e96e0b6cfdb77c4e957508315bf7b7124aea9fa1'
      user.api_key = '4a5e3a7e8aa200cbde64432df11c4b459b154498'
      self.user_controller.insert_user(user, False, True, False)

      self.apiKey = ''

      text = self.post('/login', data={'usr':'admindisabled', 'pwd':'admin'})
      if text:
        assert False
      else:
        assert True
    except HTTPError as error:
      if error.code == 403:
        assert True
      else:
        assert False
