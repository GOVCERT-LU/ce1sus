'''
Created on Jul 11, 2013

@author: jhemp
'''
import unittest
from dagr.helpers.objects import compareObjects, printObject, \
ValueMismatchException, ArrayMismatchException, printDictionary, PrintException


# pylint: disable =C0111, R0903
class Obj(object):
  def __init__(self, text, number):
    self.text = text
    self.number = number


# pylint: disable=R0904, C0111, R0201, W0612, W0613, R0915, R0903
class TestObjectHelper(unittest.TestCase):

  def testCompareBaseType(self):
    assert compareObjects(1, 1, raiseExceptions=True)
    assert compareObjects('a', 'a', raiseExceptions=True)
    assert compareObjects([1, 2], [1, 2], raiseExceptions=True)
    assert compareObjects({'foo': 1, 'bar': 2}, {'foo': 1, 'bar': 2},
                          raiseExceptions=True)
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
    except ValueMismatchException:
      assert(True)


  def testPrint(self):
    try:
      printObject(1)
      assert True
    except PrintException:
      assert False

  def testPrintDict(self):
    hashmap = {'a': 1, 'b': 2}
    printDictionary(hashmap)
    assert True

if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
