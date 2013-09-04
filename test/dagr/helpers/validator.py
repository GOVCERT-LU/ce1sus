'''
Created on Aug 7, 2013

@author: jhemp
'''
import unittest
from dagr.helpers.validator import ValueValidator, ValidationException
from datetime import datetime

class TestValidator(unittest.TestCase):


    def testAlNum(self):
      try:
        # working Tests

        assert ValueValidator.validateAlNum('Test123',
                                            minLength=0,
                                            maxLength=0,
                                            withSpaces=False,
                                            withNonPrintableCharacters=False)
        assert ValueValidator.validateAlNum('Test 123',
                                            minLength=0,
                                            maxLength=0,
                                            withSpaces=True,
                                            withNonPrintableCharacters=False)
        assert ValueValidator.validateAlNum('Test123\t11',
                                            minLength=0,
                                            maxLength=0,
                                            withSpaces=False,
                                            withNonPrintableCharacters=True)


        # NotWroking
        assert not ValueValidator.validateAlNum(u'!',
                                            minLength=0,
                                            maxLength=0,
                                            withSpaces=False,
                                            withNonPrintableCharacters=False)

        assert not ValueValidator.validateAlNum('Test 123',
                                            minLength=0,
                                            maxLength=0,
                                            withSpaces=False,
                                            withNonPrintableCharacters=False)
        assert not ValueValidator.validateAlNum('Test\t111',
                                            minLength=0,
                                            maxLength=0,
                                            withSpaces=False,
                                            withNonPrintableCharacters=False)
      except ValidationException:
        assert(False)

    def testAlpha(self):

        # working Tests
      assert ValueValidator.validateAlpha('Test',
                                            minLength=0,
                                            maxLength=0,
                                            withSpaces=False,
                                            withNonPrintableCharacters=False)
        # Not working Tests
      assert not ValueValidator.validateAlpha('Test123',
                                            minLength=0,
                                            maxLength=0,
                                            withSpaces=False,
                                            withNonPrintableCharacters=False)

    def testNumbers(self):

        # working Tests
      assert ValueValidator.validateDigits('123',
                                            minimal=None,
                                            maximal=None)
      assert ValueValidator.validateDigits('2.5',
                                            minimal=1,
                                            maximal=3)

      assert ValueValidator.validateDigits('125',
                                            minimal=125,
                                            maximal=125)

      assert ValueValidator.validateDigits(125,
                                            minimal=125,
                                            maximal=125)

        # Not working Tests
      assert not ValueValidator.validateDigits('abc',
                                            minimal=None,
                                            maximal=122)

      assert not ValueValidator.validateDigits('123',
                                            minimal=None,
                                            maximal=122)
      assert not ValueValidator.validateDigits('2.5',
                                            minimal=1,
                                            maximal=2)

      assert not ValueValidator.validateDigits(124,
                                            minimal=125,
                                            maximal=125)


    def testIP(self):

        # working Tests
      assert ValueValidator.validateIP('127.0.0.1')
        # Not working Tests
      assert not ValueValidator.validateIP('foo')


    def testEmail(self):

        # working Tests
      assert ValueValidator.validateEmailAddress('foo@foobar.com')
        # Not working Tests
      assert not ValueValidator.validateEmailAddress('foo')


    def testDate(self):

        # working Tests
      assert ValueValidator.validateDateTime('1999-01-01 - 15:00:00')
      assert ValueValidator.validateDateTime(datetime.now())
      assert ValueValidator.validateDateTime('2013-08-08 14:09:27.186303')
        # Not working Tests
      ValueValidator.validateDateTime('1999/01/01 - 15:00:00')

    def testRegex(self):
      assert ValueValidator.validateRegularExpression('^(')

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
