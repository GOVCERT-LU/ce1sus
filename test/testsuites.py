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


def suite():
  testSuite = unittest.TestSuite()
  testSuite.addTest(TestDefinitionBrokers())
  testSuite.addTest(TestEventBrokers())
  testSuite.addTest(TestPermissionBrokers())
<<<<<<< HEAD
  testSuite.addTest(TestBitDecoder())
=======
  testSuit.addTest(TestBitDecoder())
>>>>>>> 01930e5dcd9a04a5d63f5a364dd4301d929dff1e

  testSuite.addTest(TestSession())
  testSuite.addTest(TestObjectHelper())
  testSuite.addTest(TestValidator())
  testSuite.addTest(TestString())
  testSuite.addTest(Testhash())
  testSuite.addTest(TestConfiguration())
  testSuite.addTest(TestLog())
  testSuite.addTest(TestConverter())

  return testSuite


if __name__ == "__main__":
  runner = unittest.TextTestRunner()

  test_suite = suite()

  runner.run(test_suite)
