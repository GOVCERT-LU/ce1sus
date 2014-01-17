'''
Created on Aug 7, 2013

@author: jhemp
'''
import unittest
import dagr.helpers.strings as strings
from datetime import datetime


# pylint: disable=R0904, C0111, R0201, W0612, W0613, R0915, R0903, W0702, W0703
class TestString(unittest.TestCase):

  def testPlain2Html1(self):
    try:
      strings.plaintext2html('a\nb')
      strings.plaintext2html('')
      strings.plaintext2html(None)
      strings.plaintext2html(1234)
      strings.plaintext2html(datetime.now())
      assert(True)
    except:
      assert(False)

  def testDateToStirngFail(self):
    try:
      strings.stringToDateTime(datetime.now())
      assert(False)
    except Exception as e:
      print e
      assert(True)

  def testDateToStirng(self):
    try:
      strings.stringToDateTime('30/12/1999 - 23:55')
      strings.stringToDateTime('30/12/1999 23:55')
      strings.stringToDateTime('1999-01-01 - 23:55')
      strings.stringToDateTime('1999-01-01 - 23:55:55')
      strings.stringToDateTime('1999-01-01 23:55')
      assert(True)
    except Exception as e:
      print e
      assert(False)

  def testIsNull(self):
    try:
      assert(not strings.isNotNull(''))
      assert(strings.isNotNull('aaaaa'))
      assert(strings.isNotNull(123))
      assert(not strings.isNotNull(None))
      assert(strings.isNotNull(datetime.now()))
    except Exception as e:
      print e
      assert(False)

  def testStringHTML(self):
    line = 'ab\ncd'
    result = strings.plaintext2html(line)
    assert result == 'ab<br/>cd'


if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
