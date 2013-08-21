'''
Created on Jul 11, 2013

@author: jhemp
'''
import unittest
from framework.helpers.objects import compareObjects, printObject, ValueMismatchException, ArrayMismatchException, AttributeMismatchException

class Obj(object):
  def __init__(self, text, number):
    self.text = text
    self.number = number


class TestObjectHelper(unittest.TestCase):


    def testCompareBaseType(self):
      try:
        assert compareObjects(1, 1, raiseExceptions=True)
        assert compareObjects('a', 'a', raiseExceptions=True)

        assert compareObjects([1, 2], [1, 2], raiseExceptions=True)
        assert compareObjects({'foo':1, 'bar':2}, {'foo':1, 'bar':2}, raiseExceptions=True)
        assert compareObjects(1, 1, raiseExceptions=True)
        # tests with exceptions

        try:
          compareObjects('a', 'n', raiseExceptions=True)
          assert(False)
        except ValueMismatchException:
          assert(True)

        try:
          compareObjects(1, 2, raiseExceptions=True)
          assert(False)
        except ValueMismatchException:
          assert(True)
        try:
          compareObjects([1, 3], [1, 2], raiseExceptions=True)
          assert(False)
        except ValueMismatchException:
          assert(True)

        try:
          compareObjects([1, 3], [1], raiseExceptions=True)
          assert(False)
        except ArrayMismatchException:
          assert(True)

        try:
          compareObjects([1, 3], [1, 2], raiseExceptions=True)
          assert(False)
        except ValueMismatchException:
          assert(True)

        try:
          compareObjects([1, 3], [1], raiseExceptions=True)
          assert(False)
        except ArrayMismatchException:
          assert(True)



        obj1 = Obj('LoremIpsum', 1)
        obj2 = Obj('LoremIpsum', 1)
        assert compareObjects(obj1, obj2, raiseExceptions=True)
        try:
          obj1 = Obj('LoremIpsum', 1)
          obj2 = Obj('LoremIpsumFoo', 1)
          compareObjects(obj1, obj2, raiseExceptions=True)
          assert(False)
        except ValueMismatchException as e:
          assert(True)


        # boolean result
        assert not compareObjects(obj1, obj2, raiseExceptions=False)

      except Exception as e:
        print e
        assert(False)

    def testPrint(self):
      print '---- PrintTest BEGIN ----'
      printObject(1)
      print '---- PrintTest END ----'
if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
