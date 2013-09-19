'''
Created on Sep 17, 2013

@author: jhemp
'''
import unittest
from dagr.helpers.converters import ObjectConverter, ConversionException
from datetime import datetime


# pylint: disable=R0904, C0111, R0201, W0612, W0613, R0915, R0903

class TestObj(object):
  def __init__(self):
    self.int = 1
    self.str = 'None'
    self.date = datetime.now()

class TestConverter(unittest.TestCase):

  def testConversions(self):
    testObj = TestObj()
    try:
      ObjectConverter.setString(testObj, 'str', 'Test')
      assert testObj.str == 'Test'
    except ConversionException:
      assert False

    try:
      ObjectConverter.setString(testObj, 'str', '125Das')
      assert testObj.str == '125Das'
    except ConversionException:
      assert False

    try:
      ObjectConverter.setString(testObj, 'str', '125')
      assert testObj.str == '125'
    except ConversionException:
      assert False

    try:
      ObjectConverter.setInteger(testObj, 'int', 'Test')
      assert False
    except ConversionException:
      assert True

    try:
      ObjectConverter.setInteger(testObj, 'int', '55')
      assert testObj.int == 55
    except ConversionException:
      assert True
