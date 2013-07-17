'''
Created on Jul 4, 2013

@author: jhemp
'''
import unittest
import os
from ce1sus.db.session import SessionManager
from ce1sus.brokers.permissionbroker import GroupBroker, UserBroker
from ce1sus.brokers.classes.permissions import Group, User
from ce1sus.helpers.objects import compareObjects
from datetime import datetime

class TestPermissionBrokers(unittest.TestCase):

  # The following test have to be ordered

  def setUp(self):
    print os.getcwd()
    self.sessionManager = SessionManager('../ce1sus.cfg')
    self.groupbroker = self.sessionManager.brokerFactory(GroupBroker)

    self.group = Group()
    self.group.identifier = 1
    self.group.name = 'TestGroup'
    self.group.shareTLP = 0


    self.userBroker = self.sessionManager.brokerFactory(UserBroker)
    self.user = User()
    self.user.identifier = 1
    self.user.username = 'testUser'
    self.user.email = 'a@a.com'
    self.user.password = 'fooPwd'
    self.user.privileged = 0
    self.timeStamp = datetime.now()
    self.user.last_login = self.timeStamp

  def tearDown(self):
    pass


  def test_A_Insert(self):

    self.groupbroker.insert(self.group)
    assert True


  def test_B_GetGroupByID(self):
      group = self.groupbroker.getByID(self.group.identifier)
      assert compareObjects(group, self.group)

  def testNothingFound(self):
    try:
      user = self.userBroker.getUserByID('test')
      # just to prevent the warning
      print user
      assert False
    except Exception:
      assert True

  def test_C_InsertUser(self):

    # get actual group
    group = self.groupbroker.getByID(self.group.identifier)

    # attach group to user
    self.user.addGroup(group)

    self.userBroker.insert(self.user)
    assert True


# Test if the user is setup correctly if found
  def test_D_GetUserByID(self):

    user = self.userBroker.getByID(self.user.identifier)
    assert True


    assert compareObjects(user, self.user)


  def test_E_DeleteUser(self):

      #self.userBroker.removeByID(self.user.identifier)
      # Check if group is still existing
      group = self.groupbroker.getByID(self.group.identifier)

      if compareObjects(group, self.group):
        assert True
      else:
        assert False



  def test_F_DeleteGroup(self):
    #self.groupbroker.removeByID(self.group.identifier)
    pass



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
