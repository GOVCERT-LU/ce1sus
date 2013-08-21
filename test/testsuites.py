'''
Created on Jul 11, 2013

@author: jhemp
'''
import unittest
from test.ce1sus.brokers.definitionbroker import TestDefinitionBrokers
from test.ce1sus.brokers.eventbroker import TestEventBrokers
from test.ce1sus.brokers.permissionbroker import TestPermissionBrokers
from test.framework.db.session import TestSession
from test.framework.helpers.objects import TestObjectHelper
from test.framework.helpers.string import TestString
from test.framework.helpers.validator import TestValidator

def suite(self):
  suite = unittest.TestSuite()
  suite.addTest(TestDefinitionBrokers())
  suite.addTest(TestEventBrokers())
  suite.addTest(TestPermissionBrokers())
  suite.addTest(TestSession())
  suite.addTest(TestObjectHelper())
  suite.addTest(TestValidator())
  suite.addTest(TestString())

  return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()

    test_suite = suite()

    runner.run (test_suite)
