'''
Created on Jul 5, 2013

@author: jhemp
'''
import unittest
from dagr.db.session import SessionManager
from ce1sus.brokers.event.eventbroker import EventBroker
from ce1sus.brokers.event.eventclasses import Event
from datetime import datetime
from ce1sus.brokers.permission.permissionclasses import  Group, User
from ce1sus.brokers.permission.userbroker import UserBroker
from ce1sus.brokers.permission.groupbroker import GroupBroker
from dagr.helpers.objects import print_object
from ce1sus.helpers.bitdecoder import BitValue


class TestEventBrokers(unittest.TestCase):

  def setUp(self):

    self.session_manager = SessionManager('../config/ce1sustest.conf')
    self.timeStamp = datetime.now()
    # CreateNeeded Users and group
    self.groupbroker = self.session_manager.broker_factory(GroupBroker)
    self.group = Group()
    self.group.identifier = long(666)
    self.group.name = 'TestGroup'
    self.group.shareTLP = long(0)
    self.group.can_download = long(1)
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
    self.user.api_key = None
    self.user.group_id = self.group.identifier
    self.user.default_group = self.group
    self.timeStamp = datetime.now()
    self.user.disabled = long(0)
    self.user.password = 'Test$123'

    self.user.last_login = self.timeStamp
    self.eventbroker = self.session_manager.broker_factory(EventBroker)
    self.event = Event()
    # self.event.creator = self.user
    self.event.description = 'Description'
    self.event.identifier = long(666)
    self.event.created = self.timeStamp
    self.event.title = 'label'
    self.event.first_seen = self.timeStamp
    self.event.last_seen = self.timeStamp
    self.event.modified = self.timeStamp
    self.event.tlp_level_id = 1
    self.event.status_id = 1
    self.event.published = 1
    self.event.uuid = 'To be determined'
    self.event.code = BitValue('1101', self.event)
    self.event.analysis_status_id = long(0)
    self.event.risk_id = long(0)



  def tearDown(self):
    pass

  def test_0_initOnce(self):
    # this is done to populate the DB for the tests
    # create user and group
    self.groupbroker = self.session_manager.broker_factory(GroupBroker)
    self.groupbroker.insert(self.group)

    self.user_broker.insert(self.user)
    assert True

  def test_Z_lastOnce(self):
    # remove created user & group
    self.user_broker.remove_by_id(self.user.identifier)
    self.groupbroker.remove_by_id(self.group.identifier)
    assert True

  def test_C_InsertEvent(self):
    user = self.user_broker.get_by_id(self.user.identifier)

    self.event.creator_id = user.identifier
    self.creator = user
    self.event.creator = user

    self.event.modifier_id = user.identifier
    self.modfier = user

    group = self.groupbroker.get_by_id(self.group.identifier)

    self.event.creator_group = group

    self.eventbroker.insert(self.event)
    assert True

  def test_G_getID(self):
    event = self.eventbroker.get_by_id(self.event.identifier)

    assert True
    # assert helpers.compareObjects(event, self.event)

  def test_H_updateEvent(self):
    event = self.eventbroker.get_by_id(self.event.identifier)
    event.description = 'FOO LOO'
    self.eventbroker.update(event)

    event = self.eventbroker.get_by_id(self.event.identifier)


  def test_X_DeleteEvent(self):
    self.eventbroker.remove_by_id(self.event.identifier)


if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
