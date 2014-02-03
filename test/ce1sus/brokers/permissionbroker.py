'''
Created on Jul 4, 2013

@author: jhemp
'''
import unittest
import os
from dagr.db.session import SessionManager
from ce1sus.brokers.permission.groupbroker import GroupBroker
from ce1sus.brokers.permission.userbroker import UserBroker
from ce1sus.brokers.permission.permissionclasses import Group, User
from dagr.helpers.objects import compareObjects
from datetime import datetime


class TestPermissionBrokers(unittest.TestCase):

  # The following test have to be ordered

  def setUp(self):
    self.session_manager = SessionManager('../config/ce1sustest.conf')
    self.groupbroker = self.session_manager.broker_factory(GroupBroker)

    self.group = Group()
    self.group.identifier = long(666)
    self.group.name = 'TestGroup'
    self.group.shareTLP = long(0)
    self.group.canDownload = long(1)
    self.group.description = 'Description'
    self.group.email = 'a@a.com'
    self.group.usermails = long(1)
    self.user_broker = self.session_manager.broker_factory(UserBroker)
    self.user = User()
    self.user.identifier = 666
    self.user.username = 'testUser'
    self.user.email = 'a@a.com'
    self.user.password = 'fooPwd'
    self.user.privileged = 0
    self.user.apiKey = None
    self.user.group_id = self.group.identifier
    self.user.default_group = self.group
    self.timeStamp = datetime.now()
    self.user.disabled = long(0)
    self.user.password = 'Test$123'

    self.user.last_login = self.timeStamp


  def tearDown(self):
    pass

  def test_A_Insert(self):

    self.groupbroker.insert(self.group)
    assert True

  def test_B_GetGroupByID(self):
      group = self.groupbroker.get_by_id(self.group.identifier)
      assert compareObjects(group, self.group)

  def testNothingFound(self):
    try:
      user = self.user_broker.getUserByID('test')
      # just to prevent the warning
      print user
      assert False
    except Exception:
      assert True


  def test_E_DeleteUser(self):

      # self.user_broker.remove_by_id(self.user.identifier)
      # Check if group is still existing
      group = self.groupbroker.get_by_id(self.group.identifier)

      if compareObjects(group, self.group):
        assert True
      else:
        assert False

  def test_F_DeleteGroup(self):
    self.groupbroker.remove_by_id(self.group.identifier)
    pass

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
