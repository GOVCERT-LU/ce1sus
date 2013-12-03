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
    api = Ce1susAPI('http://localhost:8080/REST/0.0.0',
                    'dd94709528bb1c83d08f3088d4043f4742891f4f')
    event = api.getEventByID('147', True, True)

    printObject(event, maxRecLVL=4)
    assert True
    print "------------------------------"
    event = api.getObjectByID('134', True, True)
    printObject(event, maxRecLVL=4)
    assert True

  def testInsert(self):
    event = RestEvent()
    api = Ce1susAPI('http://localhost:8080/REST/0.1.0',
                    'dd94709528bb1c83d08f3088d4043f4742891f4f')
    event = api.getEventByID('147', True, True)
    api.insertEvent(event)
    event_orig = api.getEventByID('147', True, True)
    printObject(event, maxRecLVL=4)

    assert compareObjects(event, event_orig)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()