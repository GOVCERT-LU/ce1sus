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

  def generate_working_file(self, name):
    # generate file
    test_file = open(name, "w")
    test_file.write("[Section]\n")
    test_file.write("name=Test\n")
    test_file.write("UpperCase=Test\n")
    test_file.write("Boolean=True\n")
    test_file.write("Number=1\n")
    test_file.close()

  def generate_failing_file(self, name):
    # generate file
    test_file = open(name, "w")
    test_file.write("[Section]\n")
    test_file.write("nameTest\n")
    test_file.write("UpperCase=Test\n")
    test_file.close()

  def remove_file(self, name):
    basedir = os.path.dirname(name)
    if not os.path.exists(basedir):
      os.remove(name)

  # pylint: disable=R0912
  def test_loadIng_file(self):
    try:
      name = 'test.cfg'
      self.generate_working_file(name)
      config = Configuration(name)
      del config
      self.remove_file(name)
      assert True
    except ConfigException:
      assert False

    try:
      # missing file
      name = 'test.cfg'
      self.generate_working_file(name)
      config = Configuration(name + 'foo')
      del config
      assert False
    except ConfigFileNotFoundException:
      assert True
    except ConfigException:
      assert False
    finally:
      self.remove_file(name)

    try:
      # missing section
      name = 'test.cfg'
      self.generate_working_file(name)
      config = Configuration(name, 'Section2')
      del config
      assert False
    except ConfigSectionNotFoundException:
      assert True
    except ConfigException:
      assert False
    finally:
      self.remove_file(name)

    try:
      # missing section
      name = 'test.cfg'
      self.generate_failing_file(name)
      config = Configuration(name)
      del config
      assert False
    except ConfigParsingException:
      assert True
    except ConfigException:
      assert False
    finally:
      self.remove_file(name)

  def test_existing_section(self):
    try:
      name = 'test.cfg'
      self.generate_working_file(name)
      config = Configuration(name)
      section = config.get_section('Section')
      del section
      assert True
    except ConfigException:
      assert False
    finally:
      self.remove_file(name)

  def test_nonexisting_section(self):
    try:
      name = 'test.cfg'
      self.generate_working_file(name)
      config = Configuration(name)
      section = config.get_section('Section2')
      del section
      assert False
    except ConfigException:
      assert True
    finally:
      self.remove_file(name)

  def test_keys(self):
    try:
      name = 'test.cfg'
      self.generate_working_file(name)
      config = Configuration(name)
      section = config.get_section('Section')
      key = section.get('name')
      assert key == 'Test'
      key = section.get('UpperCase')
      assert key == 'Test'
      key = section.get('Boolean')
      assert key
      key = section.get('Number')
      assert key == 1
    except ConfigException:
      assert False
    finally:
      self.remove_file(name)

    try:
      name = 'test.cfg'
      self.generate_working_file(name)
      config = Configuration(name)
      section = config.get_section('Section')
      key = section.get('name2')
      assert False
    except ConfigKeyNotFoundException:
      assert True
    except ConfigException:
      assert False
    finally:
      self.remove_file(name)
