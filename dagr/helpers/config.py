# -*- coding: utf-8 -*-

"""
configuration module

Created: Jul, 2103
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ConfigParser import ConfigParser, Error, ParsingError
from os.path import isfile
from os import getcwd

class ConfigException(Exception):
  """Configuration Exception"""

  def __init__(self, message):
    Exception.__init__(self, message)

class ConfigParsingException(ConfigException):
  """ConfigFileNotFoundException Exception"""

  def __init__(self, message):
    ConfigException.__init__(self, message)


class ConfigFileNotFoundException(ConfigException):
  """ConfigFileNotFoundException Exception"""

  def __init__(self, message):
    ConfigException.__init__(self, message)

class ConfigSectionNotFoundException(ConfigException):
  """ConfigFileNotFoundException Exception"""

  def __init__(self, message):
    ConfigException.__init__(self, message)

class ConfigKeyNotFoundException(ConfigException):
  """ConfigFileNotFoundException Exception"""

  def __init__(self, message):
    ConfigException.__init__(self, message)

# pylint: disable=C0111, R0903
class Configuration(object):
  """Configuration class"""

  def __init__(self, configFile, section):
    self.configDict = dict()
    config = ConfigParser()
    if not isfile(configFile):
      raise ConfigFileNotFoundException('Could not find config file ' +
                            configFile + ' in ' + getcwd())
    try:
      config.read(configFile)
    except ParsingError as e:
      raise ConfigParsingException(e)

    if config.has_section(section):
      options = config.options(section)
      for option in options:
        try:
          string = config.get(section, option)
          function = getattr(string, 'upper')
          if function() in ['YES', 'NO', 'TRUE', 'FALSE']:
            self.configDict[option] = config.getboolean(section, option)
          else:
            function = getattr(string, 'isdigit')
            if function():
              self.configDict[option] = config.getint(section, option)
            else:
              self.configDict[option] = string
        except Error as e:
          raise ConfigException(e)
    else:
      raise ConfigSectionNotFoundException('Section ' + section +
                                           ' is not found in ' + configFile)

  def get(self, identifier):
    """
    Returns the value for the given identifier

    :returns: Any
    """
    try:
      return self.configDict[identifier.lower()]
    except KeyError:
      raise ConfigKeyNotFoundException('Key ' + identifier + ' not found.')
