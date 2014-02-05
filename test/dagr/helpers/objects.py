'''
Created on Jul 11, 2013

@author: jhemp
'''
import unittest
from dagr.helpers.objects import compare_objects, print_object, \
ValueMismatchException, ArrayMismatchException, print_dictionary, PrintException


# pylint: disable =C0111, R0903
class Obj(object):
  def __init__(self, text, number):
    self.text = text
    self.number = number


# pylint: disable=R0904, C0111, R0201, W0612, W0613, R0915, R0903
class TestObjectHelper(unittest.TestCase):

  def testCompareBaseType(self):
    assert compare_objects(1, 1, raise_exceptions=True)
    assert compare_objects('a', 'a', raise_exceptions=True)
    assert compare_objects([1, 2], [1, 2], raise_exceptions=True)
    assert compare_objects({'foo': 1, 'bar': 2}, {'foo': 1, 'bar': 2},
                          raise_exceptions=True)
    assert compare_objects(1, 1, raise_exceptions=True)
    # tests with exceptions

    try:
      compare_objects('a', 'n', raise_exceptions=True)
      assert(False)
    except ValueMismatchException:
      assert(True)

    try:
      compare_objects(1, 2, raise_exceptions=True)
      assert(False)
    except ValueMismatchException:
      assert(True)
    try:
      compare_objects([1, 3], [1, 2], raise_exceptions=True)
      assert(False)
    except ValueMismatchException:
      assert(True)

    try:
      compare_objects([1, 3], [1], raise_exceptions=True)
      assert(False)
    except ArrayMismatchException:
      assert(True)

    try:
      compare_objects([1, 3], [1, 2], raise_exceptions=True)
      assert(False)
    except ValueMismatchException:
      assert(True)

    try:
      compare_objects([1, 3], [1], raise_exceptions=True)
      assert(False)
    except ArrayMismatchException:
      assert(True)

    obj1 = Obj('LoremIpsum', 1)
    obj2 = Obj('LoremIpsum', 1)
    assert compare_objects(obj1, obj2, raise_exceptions=True)
    try:
      obj1 = Obj('LoremIpsum', 1)
      obj2 = Obj('LoremIpsumFoo', 1)
      compare_objects(obj1, obj2, raise_exceptions=True)
      assert(False)
    except ValueMismatchException:
      assert(True)


  def testPrint(self):
    try:
      print_object(1)
      assert True
    except PrintException:
      assert False

  def testPrintDict(self):
    hashmap = {'a': 1, 'b': 2}
    print_dictionary(hashmap)
    assert True

if __name__ == "__main__":
  # import sys;sys.argv = ['', 'Test.testName']
  unittest.main()
