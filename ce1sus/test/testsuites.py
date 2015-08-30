# -*- coding: utf-8 -*-

'''
Created on Jul 11, 2013

@author: jhemp
'''
import unittest

from ce1sus.test.admin.adminattributes import TestAdminAttributes
from ce1sus.test.admin.adminconditions import TestAdminCondition
from ce1sus.test.admin.admingroups import TestAdminGroups
from ce1sus.test.admin.adminmails import TestAdminMailTemplates
from ce1sus.test.admin.adminobjects import TestAdminObjects
from ce1sus.test.admin.adminreference import TestAdminReferences
from ce1sus.test.admin.adminsyncserver import TestAdminSyncServers
from ce1sus.test.admin.admintypes import TestAdminTypes
from ce1sus.test.admin.adminuser import TestAdminUsers
from ce1sus.test.event.event import TestEvent
from ce1sus.test.event.object import TestObject
from ce1sus.test.event.observable import TestObservable
from ce1sus.test.login import TestLogin
from ce1sus.test.mappers.misp import TestMisp


def suite():
  testSuite = unittest.TestSuite()
  testSuite.addTest(TestLogin())
  testSuite.addTest(TestAdminAttributes())
  testSuite.addTest(TestAdminObjects())
  testSuite.addTest(TestAdminReferences())
  testSuite.addTest(TestAdminCondition())
  testSuite.addTest(TestAdminTypes())
  testSuite.addTest(TestAdminMailTemplates())
  testSuite.addTest(TestAdminGroups())
  testSuite.addTest(TestAdminSyncServers())
  testSuite.addTest(TestAdminUsers())
  testSuite.addTest(TestEvent())
  testSuite.addTest(TestObservable())
  testSuite.addTest(TestObject())
  testSuite.addTest(TestMisp())
  return testSuite


if __name__ == "__main__":
  runner = unittest.TextTestRunner()

  test_suite = suite()

  runner.run(test_suite)
