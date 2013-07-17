'''
Created on Jul 11, 2013

@author: jhemp
'''
import unittest
from ce1sus.helpers.objects import compareObjects, printObject

class Obj(object):
  def __init__(self, text, number):
    self.text = text
    self.number = number
  

class TestObjectHelper(unittest.TestCase):


    def testCompareBaseType(self):
      assert compareObjects(1,1)
      assert compareObjects('a','a')
      
      assert compareObjects([1,2],[1,2])
      assert compareObjects({'foo':1,'bar':2},{'foo':1,'bar':2})
      
      assert not compareObjects('a','n')
      assert not compareObjects(1,2)
      assert not compareObjects([1,3],[1,2])
      assert not compareObjects({'foo':1,'bar':3},{'foo':1,'bar':2})
      
      obj1 = Obj('LoremIpsum',1)
      obj2 = Obj('LoremIpsum',1)
      assert compareObjects(obj1, obj2)
    
      obj1 = Obj('LoremIpsum',1)
      obj2 = Obj('LoremIpsumFoo',1)
      assert not compareObjects(obj1, obj2)
    def testPrint(self):
      printObject(1)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()