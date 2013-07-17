'''
Created on Jul 11, 2013

@author: jhemp
'''
import unittest
from test.ce1sus.brokers.definitionbroker import TestDefinitionBrokers
from test.ce1sus.brokers.eventbroker import TestEventBrokers
from test.ce1sus.brokers.permissionbroker import TestPermissionBrokers
from test.ce1sus.db.session import TestSession
from test.ce1sus.helpers.objects import TestObjectHelper

def suite(self):
  suite = unittest.TestSuite()
  suite.addTest(TestDefinitionBrokers())
  suite.addTest(TestEventBrokers())
  suite.addTest(TestPermissionBrokers())
  suite.addTest(TestSession())
  suite.addTest(TestObjectHelper())
  return suite


if __name__ == "__main__":
    runner = unittest.TextTestRunner()

    test_suite = suite()

    runner.run (test_suite)