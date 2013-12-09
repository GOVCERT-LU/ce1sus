'''
Created on Oct 29, 2013

@author: jhemp
'''
import unittest
from dagr.helpers.objects import printObject, compareObjects
from ce1sus.api.ce1susapi import Ce1susAPI
from ce1sus.api.restclasses import RestEvent


# pylint:disable=R0904
class Test(unittest.TestCase):

  def testName(self):
    api = Ce1susAPI('http://localhost:8080/REST/0.1.0',
                    '5abc424daa7448af9c4a249036dbd064a2a9a087')
    event = api.getEventByUUID('43ecf6c4-d25b-4862-9b63-4bc17125fc70', True)

    printObject(event, maxRecLVL=4)
    assert True
    api.insertEvent(event)
    print "------------------------------"
    event = api.getObjectByID('231', True, True)
    printObject(event, maxRecLVL=4)
    assert True

  def testInsert(self):
    event = RestEvent()
    api = Ce1susAPI('http://localhost:8080/REST/0.1.0',
                    'dd94709528bb1c83d08f3088d4043f4742891f4f')
    event = api.getEventByUUID('147', True, True)
    api.insertEvent(event)
    event_orig = api.getEventByUUID('147', True, True)
    printObject(event, maxRecLVL=4)

    assert compareObjects(event, event_orig)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
