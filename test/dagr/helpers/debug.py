'''
Created on Sep 17, 2013

@author: jhemp
'''
import unittest
import os
from dagr.helpers.debug import Log
from dagr.helpers.config import ConfigFileNotFoundException, \
ConfigParsingException

# pylint: disable=R0904, C0111, R0201, W0612, W0613, R0915, R0903
class TestLog(unittest.TestCase):

  def generateConfig(self, name, sectionName='Logger', writeSection=True):
    testFile = open(name, "w")
    if writeSection:
      testFile.write("[{0}]\n".format(sectionName))
    testFile.write("log=Yes\n")
    testFile.write("logfile=logger.txt\n")
    testFile.write("logConsole = Yes\n")
    testFile.write("level=DEBUG\n")
    testFile.write("size=10000000\n")
    testFile.write("backups=1000\n")
    testFile.close()

  def removeFile(self, name):
    basedir = os.path.dirname(name)
    if not os.path.exists(basedir):
      os.remove(name)


  def testSetup(self):

    # load without config
    Log.getInstance()
    assert True

    # load with config
    name = 'test.cfg'
    try:
      self.generateConfig(name)
      Log(name)
      Log.getLogger('TestLog').debug('haha')
      assert True
    except:
      assert False
    finally:
      self.removeFile(name)
      self.removeFile('logger.txt')


    # load with no file config
    name = 'test2.cfg'
    try:
      Log(name)
      assert False
    except ConfigFileNotFoundException:
      assert True

    # load with no erronous file config
    name = 'test.cfg'
    try:
      self.generateConfig(name, writeSection=False)
      Log(name)
      assert False
    except ConfigParsingException:
      assert True
    finally:
      self.removeFile(name)

      # load with no erronous file config
    name = 'test.cfg'
    try:
      self.generateConfig(name, sectionName='haaha', writeSection=False)
      Log(name)
      assert False
    except ConfigParsingException:
      assert True
    finally:
      self.removeFile(name)

