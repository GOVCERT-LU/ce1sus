'''
Created on Sep 17, 2013

@author: jhemp
'''

import unittest
import os
from dagr.helpers.config import Configuration, ConfigException, \
 ConfigFileNotFoundException, ConfigSectionNotFoundException, \
 ConfigKeyNotFoundException, ConfigParsingException

# pylint: disable=R0904, C0111, R0201, W0612, W0613, R0915, R0903
class TestConfiguration(unittest.TestCase):

  def generateWorkingFile(self, name):
    # generate file
    testFile = open(name, "w")
    testFile.write("[Section]\n")
    testFile.write("name=Test\n")
    testFile.write("UpperCase=Test\n")
    testFile.write("Boolean=True\n")
    testFile.write("Number=1\n")
    testFile.close()

  def generateFailingFile(self, name):
    # generate file
    testFile = open(name, "w")
    testFile.write("[Section]\n")
    testFile.write("nameTest\n")
    testFile.write("UpperCase=Test\n")
    testFile.close()

  def removeFile(self, name):
    basedir = os.path.dirname(name)
    if not os.path.exists(basedir):
      os.remove(name)

  # pylint: disable=R0912
  def testLoadIngFile(self):
    try:
      name = 'test.cfg'
      self.generateWorkingFile(name)
      config = Configuration(name, 'Section')
      del config
      self.removeFile(name)
      assert True
    except ConfigException:
      assert False

    try:
      # missing file
      name = 'test.cfg'
      self.generateWorkingFile(name)
      config = Configuration(name + 'foo', 'Section')
      del config
      assert False
    except ConfigFileNotFoundException:
      assert True
    except ConfigException:
      assert False
    finally:
      self.removeFile(name)

    try:
      # missing section
      name = 'test.cfg'
      self.generateWorkingFile(name)
      config = Configuration(name, 'Section2')
      del config
      assert False
    except ConfigSectionNotFoundException:
      assert True
    except ConfigException:
      assert False
    finally:
      self.removeFile(name)

    try:
      # missing section
      name = 'test.cfg'
      self.generateFailingFile(name)
      config = Configuration(name, 'Section')
      del config
      assert False
    except ConfigParsingException:
      assert True
    except ConfigException:
      assert False
    finally:
      self.removeFile(name)


  def testKeys(self):
    try:
      name = 'test.cfg'
      self.generateWorkingFile(name)
      config = Configuration(name, 'Section')
      key = config.get('name')
      assert key == 'Test'
      key = config.get('UpperCase')
      assert key == 'Test'
      key = config.get('Boolean')
      assert key
      key = config.get('Number')
      assert key == 1
    except ConfigException:
      assert False
    finally:
      self.removeFile(name)

    try:
      name = 'test.cfg'
      self.generateWorkingFile(name)
      config = Configuration(name, 'Section')
      key = config.get('name2')
      assert False
    except ConfigKeyNotFoundException:
      assert True
    except ConfigException:
      assert False
    finally:
      self.removeFile(name)

