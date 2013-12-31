# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 29, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import unittest
from ce1sus.api.ce1susapi import Ce1susAPI, Ce1susAPIException, Ce1susForbiddenException, Ce1susNothingFoundException, Ce1susAPIConnectionException, Ce1susInvalidParameter, Ce1susForbiddenException, Ce1susUnkownDefinition
from ce1sus.api.restclasses import RestEvent, RestObject, RestObjectDefinition, RestAttribute, RestAttributeDefinition
from dagr.helpers.datumzait import datumzait
from dagr.helpers.objects import compareObjects
from dagr.helpers.string import stringToDateTime
from datetime import datetime


# pylint:disable=R0904
class TestAPI(unittest.TestCase):

  URL = 'https://ce1sus-dev.int.govcert.etat.lu/REST/0.2.0'
  # URL = 'http://localhost:8080/REST/0.2.0'
  APIKEY = '646a4ed8aa4808a548835f7b4640280abfa2d289'

  def setUp(self):
    self.api = Ce1susAPI(TestAPI.URL, TestAPI.APIKEY)

  def tearDown(self):
    pass

  @staticmethod
  def __generateEvent():
    event = RestEvent()
    event.title = 'Test Event 1'
    event.description = 'This is a test event and has no extra meaning'
    event.first_seen = stringToDateTime('2013-12-13 14:41:01+00:00')
    event.last_seen = stringToDateTime('2013-12-13 14:41:01+00:00')
    event.tlp = 'Red'
    event.risk = 'None'
    event.analysis = 'None'
    event.objects = list()
    event.comments = list()
    event.published = 1
    event.status = 'Deleted'

    # attach some objects
    obj = RestObject()
    obj.definition = RestObjectDefinition()
    obj.definition.name = 'executable_file'
    obj.definition.description = 'executable_file\r\n\r\nThis includes all kind of compiled code'
    obj.definition.chksum = 'f82c52727e0d45c79cd3810704314d6c08fed47a'
    obj.attributes = list()
    obj.parent = None
    obj.children = list()

    # object Attributes
    attribute = RestAttribute()
    attribute.definition = RestAttributeDefinition()
    attribute.definition.name = 'file_name'
    attribute.definition.description = 'The file_name field specifies the name of the file.'
    attribute.definition.regex = '^.+$'
    attribute.definition.classIndex = 1
    attribute.definition.handlerIndex = 0
    attribute.definition.chksum = '9802f41df84b79d361e9aafe62386299a77c76f8'
    attribute.value = 'MaliciousTest.exe'
    attribute.ioc = 1

    obj.attributes.append(attribute)

    child = RestObject()
    child.definition = RestObjectDefinition()
    child.definition.name = 'forensic_records'
    child.definition.description = 'forensic_records'
    child.definition.dbchksum = 'fc771f573182da23515be31230903ec2c45e8a3a'
    child.attributes = list()
    child.parent = None
    child.children = list()

    attribute = RestAttribute()
    attribute.definition = RestAttributeDefinition()
    attribute.definition.name = 'description'
    attribute.definition.description = 'Contains free text description for an object'
    attribute.definition.regex = '^.+$'
    attribute.definition.classIndex = 0
    attribute.definition.handlerIndex = 9
    attribute.definition.chksum = 'b248f7d94db2e4da5188d7d8ba242f23ba733012'
    attribute.value = 'This is a description!'
    attribute.ioc = 0

    obj.children.append(child)
    event.objects.append(obj)

    child.attributes.append(attribute)

    return event

  def test_A_noconnection(self):
    api = Ce1susAPI('http://dontexist:8080/REST/0.2.0', 'SomeKey')
    try:

      api.getEventByUUID('9e299a5a-9591-4f11-a51f-8d0d11d37f80')
      assert False
    except Ce1susAPIConnectionException:
      assert True
    except Ce1susAPIException:
      assert False
    del api

  def test_B_Unauthorized_Get(self):
    api = Ce1susAPI(TestAPI.URL, 'SomeKey2')
    try:
      api = Ce1susAPI(TestAPI.URL, 'SomeKey2')
      api.getEventByUUID('9e299a5a-9591-4f11-a51f-8d0d11d37f80')
      assert False
    except Ce1susForbiddenException:
      assert True
    except Ce1susAPIException:
      assert False
    del api

  def test_B_Unauthorized_insert(self):
    api = Ce1susAPI(TestAPI.URL, 'SomeKey')
    try:

      event = TestAPI.__generateEvent()
      api.insertEvent(event)
      assert False
    except Ce1susForbiddenException:
      assert True
    except Ce1susAPIException as e:
      print e
      assert False
    del api

  def test_C1_Authorized_Get_InvalidUUID(self):
    try:
      # this is not a valid uuid
      self.api.getEventByUUID('Something')
      assert False
    except Ce1susNothingFoundException:
      assert False
    except Ce1susInvalidParameter:
      assert True
    except Ce1susAPIException:
      assert False

  def test_C1b_Authorized_Get_NotFound(self):
    try:
      # this is a valid uuid but not found
      self.api.getEventByUUID('32016ddc-1b61-41e7-a563-2d9e27ad798b')
      assert False
    except Ce1susNothingFoundException:
      assert True
    except Ce1susInvalidParameter:
      assert False
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C2_Authorized_insert(self):

    try:
      event = TestAPI.__generateEvent()
      returnEvent = self.api.insertEvent(event, True)
      uuidValue = returnEvent.uuid
      returnEvent = self.api.getEventByUUID(uuidValue, withDefinition=True)
      returnEvent.uuid = None
      assert (compareObjects(event, returnEvent))
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C3_Authorized_Insert_SpecialChars(self):
    try:
      event = TestAPI.__generateEvent()
      event.title = 'TitleWithSpecialChar' + u'\u2019'
      event.uuid = None
      returnEvent = self.api.insertEvent(event, True)
      uuidValue = returnEvent.uuid
      returnEvent = self.api.getEventByUUID(uuidValue, withDefinition=True)
      returnEvent.uuid = None
      assert (compareObjects(event, returnEvent))
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C4_Authorized_getEvents(self):
    try:
      events = self.api.getEvents()
      # just checking if the number of events is as expected
      assert len(events) == 16
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C5_Authorized_getEvents(self):
    try:
      uuidlist = ['c26a2e2a-655f-452b-b2b7-30aea2f7d1cc', '37cda72e-0729-488e-bb45-11d11fcfc41a', 'cebe6f4b-56a1-40f9-8e16-577c94c16343']
      events = self.api.getEvents(uuids=uuidlist)
      # just checking if the number of events is as expected
      assert len(events) == 3
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C5_Authorized_getDefinitions(self):
    try:
      adefinitions = self.api.getAttributeDefinitions()
      odefinitions = self.api.getObjectDefinitions()
      assert len(adefinitions) == 104
      assert len(odefinitions) == 13
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C5b_Authorized_getEvents(self):
    try:
      uuidlist = ['c26a2e2a-655f-452b-b2b7-30aea2f7d1cc', '37cda72e-0729-488e-bb45-11d11fcfc41a', 'cebe6f4b-56a1-40f9-8e16-577c94c16343']
      events = self.api.getEvents(uuids=uuidlist, offset=0,
                limit=1)
      # just checking if the number of events is as expected
      assert len(events) == 1
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C5c_Authorized_getEvents(self):
    try:
      uuidlist = ['c26a2e2a-655f-452b-b2b7-30aea2f7d1cc', '37cda72e-0729-488e-bb45-11d11fcfc41a', 'cebe6f4b-56a1-40f9-8e16-577c94c16343']
      events = self.api.getEvents(uuids=uuidlist, offset=1,
                limit=1)
      # just checking if the number of events is as expected
      assert len(events) == 1
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C5d_Authorized_getEvents(self):
    try:
      uuidlist = ['c26a2e2a-655f-452b-b2b7-30aea2f7d1cc', '37cda72e-0729-488e-bb45-11d11fcfc41a', 'cebe6f4b-56a1-40f9-8e16-577c94c16343']
      events = self.api.getEvents(uuids=uuidlist, offset=3,
                limit=1)
      # just checking if the number of events is as expected
      assert len(events) == 0
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C5c_Authorized_getEvents(self):
    try:
      uuidlist = ['c26a2e2a-655f-452b-b2b7-30aea2f7d1cc', '37cda72e-0729-488e-bb45-11d11fcfc41a', 'cebe6f4b-56a1-40f9-8e16-577c94c16343']
      events = self.api.getEvents(uuids=uuidlist, startDate=datetime.now())
      # just checking if the number of events is as expected
      assert len(events) == 0
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C7_search(self):
    try:
      attributes = list()
      # get all uuids where md5 is like this
      attributes.append({'hash_md5':'b29a4ddf98aee13f226258a8fab7d577'})
      events = self.api.searchEventsUUID(objectType='generic_file', objectContainsAttribute=attributes)
      assert len(events) == 1
      assert events[0] == '8454e6da-0c44-4617-aedb-bc8604715e7f'
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C8_search(self):
    try:
      attributes = list()
      # get all uuids where md5 is like this
      attributes.append({'hash_md5':'b29a4ddf98aee13f226258a8fab7d577'})
      filterAttributes = list()
      filterAttributes.append('mime_type')
      events = self.api.searchAttributes(objectContainsAttribute=attributes, filterAttributes=filterAttributes, withDefinition=True)

      assert len(events) == 1
      assert events[0].uuid == '8454e6da-0c44-4617-aedb-bc8604715e7f'
      assert len(events[0].objects) == 1
      assert len(events[0].objects[0].attributes) == 1
      assert events[0].objects[0].attributes[0].definition.name == 'mime_type'
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C9_eventsevents(self):
    try:
      uuidlist = ['fc54c7e1-69c6-44f3-84c9-b957dbbfe256']
      events = self.api.getEvents(uuids=uuidlist)
      # just checking if the number of events is as expected
      assert len(events) == 1
      events = self.api.getEventByUUID('fc54c7e1-69c6-44f3-84c9-b957dbbfe256')
      assert True
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C10_Authorized_getDefinitionWithRelation(self):
    try:
      chksums = list()
      chksums.append('a88b7dcd1a9e3e17770bbaa6d7515b31a2d7e85d')
      odefinitions = self.api.getObjectDefinitions(chksums=chksums,
                                                   withDefinition=True)
      assert odefinitions
      assert len(odefinitions) == 1
      assert len(odefinitions[0].attributes) == 32
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C10b_Authorized_getDefinitionWithRelation(self):
    try:
      chksums = list()
      chksums.append('b526d4aadf8c5af2637d5c73d5030682889af1b9')
      adefinitions = self.api.getAttributeDefinitions(chksums=chksums,
                                                      withDefinition=True)
      assert adefinitions
      assert len(adefinitions) == 1
      assert len(adefinitions[0].objects) == 5
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C11_Authorized_getDefinitionWithoutRelation(self):
    try:
      chksums = list()
      chksums.append('a88b7dcd1a9e3e17770bbaa6d7515b31a2d7e85d')
      odefinitions = self.api.getObjectDefinitions(chksums=chksums,
                                                   withDefinition=False)
      assert odefinitions
      assert len(odefinitions) == 1
      assert not odefinitions[0].attributes
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C11b_Authorized_getDefinitionWithoutRelation(self):
    try:
      chksums = list()
      chksums.append('b526d4aadf8c5af2637d5c73d5030682889af1b9')
      adefinitions = self.api.getAttributeDefinitions(chksums=chksums,
                                                      withDefinition=False)
      assert adefinitions
      assert len(adefinitions) == 1
      assert not adefinitions[0].objects
    except Ce1susAPIException as e:
      print e
      assert False

  def test_C12_autorizedGetEventsEvent(self):
    # test if a user can get access events of a group which he doesn't belong to

    api = Ce1susAPI(TestAPI.URL,
                    'e0a9208bd4b5b79b902de528cd0245bb576a99cc')
    # get a single event
    try:
      api.getEventByUUID('9e299a5a-9591-4f11-a51f-8d0d11d37f80')
      assert False
    except Ce1susForbiddenException:
      assert True
    except Ce1susAPIException as e:
      print e
      assert False

    # get all events
    try:
      events = api.getEvents()
      assert not events
    except Ce1susForbiddenException:
      assert False
    except Ce1susAPIException as e:
      assert False
    del api


  def test_C13_insertDefinition(self):
    definition = RestObjectDefinition()
    definition.name = 'test_object'
    definition.description = 'test description'
    # the checksum will be computed anyway on the server side
    definition.chksum = None
    try:
      result = self.api.insertObjectDefinition(definition, True)
    except Ce1susAPIException as e:
      assert False

    adefinition = RestAttributeDefinition()
    adefinition.name = 'Test_attribute'
    adefinition.description = 'test description'
    adefinition.regex = '^.+$'
    adefinition.classIndex = 0
    adefinition.handlerIndex = 9
    adefinition.chksum = 'b248f7d94db2e4da5188d7d8ba242f23ba733012'
    adefinition.relation = 0

    definition.attributes = list()
    definition.attributes.append(adefinition)
    try:
      result = self.api.insertObjectDefinition(definition, True)
    except Ce1susAPIException as e:
      assert False

  def test_C13b_insertDefinitionWithFalutyIndexes(self):
    definition = RestObjectDefinition()
    definition.name = 'test_object'
    definition.description = 'test description'
    # the checksum will be computed anyway on the server side
    definition.chksum = None
    try:
      result = self.api.insertObjectDefinition(definition, True)
    except Ce1susAPIException as e:
      assert False

    adefinition = RestAttributeDefinition()
    adefinition.name = 'Test_attribute'
    adefinition.description = 'test description'
    adefinition.regex = '^.+$'
    adefinition.classIndex = 0
    adefinition.handlerIndex = 20
    adefinition.chksum = 'b248f7d94db2e4da5188d7d8ba242f23ba733012'
    adefinition.relation = 0

    definition.attributes = list()
    definition.attributes.append(adefinition)
    try:
      result = self.api.insertObjectDefinition(definition, True)
      assert False
    except Ce1susUnkownDefinition as e:
      assert True
    except Ce1susAPIException as e:
      assert False
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
