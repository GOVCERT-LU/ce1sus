'''
Created on Jul 11, 2013

@author: jhemp
'''
import unittest
from test.dagr.db.session import TestSession
from test.dagr.helpers.objects import TestObjectHelper
from test.dagr.helpers.string import TestString
from test.dagr.helpers.validator import TestValidator
from test.dagr.helpers.hash import Testhash
from test.dagr.helpers.config import TestConfiguration
from test.dagr.helpers.debug import TestLog
from test.dagr.helpers.converters import TestConverter
from test.ce1sus.brokers.definitionbroker import TestDefinitionBrokers
from test.ce1sus.brokers.permissionbroker import TestPermissionBrokers
from test.ce1sus.brokers.eventbroker import TestEventBrokers
from test.ce1sus.helpers.bitdecoder import TestBitDecoder
from test.ce1sus.api.ce1susapi import TestAPI


def suite():
  testSuite = unittest.TestSuite()
  testSuite.addTest(TestDefinitionBrokers())
  testSuite.addTest(TestEventBrokers())
  testSuite.addTest(TestPermissionBrokers())
  testSuite.addTest(TestBitDecoder())

  testSuite.addTest(TestSession())
  testSuite.addTest(TestObjectHelper())
  testSuite.addTest(TestValidator())
  testSuite.addTest(TestString())
  testSuite.addTest(Testhash())
  testSuite.addTest(TestConfiguration())
  testSuite.addTest(TestLog())
  testSuite.addTest(TestConverter())
  testSuite.addTest(TestAPI())

  return testSuite


if __name__ == "__main__":
  runner = unittest.TextTestRunner()

  test_suite = suite()

  runner.run(test_suite)
