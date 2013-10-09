'''
Created on Jul 5, 2013

@author: jhemp
'''
import unittest
from dagr.db.session import SessionManager
from ce1sus.brokers.eventbroker import EventBroker, ObjectBroker, \
  AttributeBroker, Event, Object, Attribute
from datetime import datetime
from ce1sus.brokers.permissionbroker import GroupBroker, UserBroker, Group, User
from ce1sus.brokers.definitionbroker import AttributeDefinitionBroker, \
  ObjectDefinitionBroker, ObjectDefinition, AttributeDefinition
from dagr.helpers.objects import printObject


class TestEventBrokers(unittest.TestCase):

  def setUp(self):

    self.sessionManager = SessionManager('../ce1sus.cfg')
    self.timeStamp = datetime.now()
    # CreateNeeded Users and group
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
    self.eventbroker = self.sessionManager.brokerFactory(EventBroker)
    self.event = Event()
    # self.event.creator = self.user
    self.event.description = 'Description'
    self.event.identifier = 1
    self.event.created = self.timeStamp
    self.event.title = 'label'
    self.event.first_seen = self.timeStamp
    self.event.last_seen = self.timeStamp
    self.event.modified = self.timeStamp
    self.event.tlp_level_id = 1
    self.event.status_id = 1
    self.event.published = 1

    self.defObjectBroker = self.sessionManager.brokerFactory(ObjectDefinitionBroker)
    self.defObj = ObjectDefinition()
    self.defObj.identifier = 1
    self.defObj.description = 'Description'
    self.defObj.name = 'Name'

    self.defAttributeBroker = self.sessionManager.brokerFactory(AttributeDefinitionBroker)
    self.defattribute = AttributeDefinition()
    self.defattribute.identifier = 1
    self.defattribute.description = 'Description'
    self.defattribute.name = 'name'
    self.defattribute.regex = 'tege'
    self.defattribute.classIndex = 1
    self.attributeBroker = self.sessionManager.brokerFactory(AttributeBroker)
    self.objectBroker = self.sessionManager.brokerFactory(ObjectBroker)
    self.obj = Object()
    self.obj.identifier = 1
    self.obj.tlp_level = 1
    self.attribute = Attribute()
    self.attribute.identifier = 1
    self.attribute.value = 'Test'

  def tearDown(self):
    pass

  def test_0_initOnce(self):
    # this is done to populate the DB for the tests
    # create user and group
    self.groupbroker = self.sessionManager.brokerFactory(GroupBroker)
    self.groupbroker.insert(self.group)

    group = self.groupbroker.getByID(self.group.identifier)
    self.user.addGroup(group)
    self.userBroker.insert(self.user)

  def test_Z_lastOnce(self):
    # remove created user & group
    self.userBroker.removeByID(self.user.identifier)
    self.groupbroker.removeByID(self.group.identifier)

  def test_A_InsertDef_ObjectAndAttribute(self):
    self.defObjectBroker.insert(self.defObj)
    self.defAttributeBroker.insert(self.defattribute)

  def test_C_InsertEvent(self):
    user = self.userBroker.getByID(self.user.identifier)
    self.event.creator_id = user.identifier
    self.creator = user
    self.event.creator = user

    self.eventbroker.insert(self.event)

    # generatte object
    self.obj.creator = user
    self.obj.creator_id = user.identifier
    self.obj.definition = self.defObjectBroker.getByID(self.defObj.identifier)
    self.obj.def_object_id = self.defObj.identifier
    self.obj.event_id = self.event.identifier

    self.objectBroker.insert(self.obj)

    # generate attribute
    self.attribute.creator = user
    self.attribute.creator_id = user.identifier
    self.attribute.definition = self.defAttributeBroker.getByID(self.defattribute.identifier)
    self.attribute.def_attribute_id = self.defattribute.identifier
    self.attribute.object = self.obj
    self.attribute.object_id = self.obj
    self.attribute.value = 'Text'
    self.attributeBroker.insert(self.attribute)
    self.event.addObject(self.obj)
    self.eventbroker.insert(self.event)

  def test_G_getID(self):
    event = self.eventbroker.getByID(self.event.identifier)
    printObject(event)
    # assert helpers.compareObjects(event, self.event)

  def test_H_updateEvent(self):
    event = self.eventbroker.getByID(self.event.identifier)
    event.description = 'FOO LOO'
    self.eventbroker.update(event)

    event = self.eventbroker.getByID(self.event.identifier)

    printObject(event)

  def test_X_DeleteEvent(self):
    self.objectBroker.removeByID(self.obj.identifier)
    self.eventbroker.removeByID(self.event.identifier)

  def test_Y_deleteDef_ObjectAndAttribute(self):
    self.defAttributeBroker.removeByID(self.defattribute.identifier)
    self.defObjectBroker.removeByID(self.defObj.identifier)

if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
