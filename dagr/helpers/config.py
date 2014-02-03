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
from dagr.helpers.strings import convert_to_value


class ConfigException(Exception):
  """Configuration Exception"""
  pass


class ConfigParsingException(ConfigException):
  """ConfigFileNotFoundException Exception"""
  pass


class ConfigFileNotFoundException(ConfigException):
  """ConfigFileNotFoundException Exception"""
  pass


class ConfigSectionNotFoundException(ConfigException):
  """ConfigFileNotFoundException Exception"""
  pass


class ConfigKeyNotFoundException(ConfigException):
  """ConfigFileNotFoundException Exception"""
  pass


# pylint: disable=C0111, R0903
class Configuration(object):
  """Configuration class"""

  def __init__(self, config_file):
    self.config_parser = ConfigParser()
    self.config_file = config_file
    if not isfile(config_file):
      raise ConfigFileNotFoundException('Could not find config file ' +
                            config_file + ' in ' + getcwd())
    try:
      self.config_parser.read(config_file)
    except ParsingError as error:
      raise ConfigParsingException(error)
    self.__seen_sections = dict()

  def __process_section(self, section):
    """
    Process the items of the section an converts it to the correct values

    :param section: name of the section
    :type section: String

    :returns: Dictionary
    """
    options = self.config_parser.options(section)
    result = dict()
    for option in options:
      try:
        string = self.config_parser.get(section, option)
        result[option] = convert_to_value(string)
      except Error as error:
        raise ConfigException(error)
    return result

  def get_section(self, section):
    """
    Returns the values of the section

    :param section: name of the section
    :type section: String

    :returns: Dictionary
    """
    # check if section was not already seen
    if section in self.__seen_sections.keys():
      return self.__seen_sections.get(section)
    elif self.config_parser.has_section(section):
      items = self.__process_section(section)
      # store items
      self.__seen_sections[section] = items
      return items
    else:
      raise ConfigSectionNotFoundException('Section ' + section +
                                             ' is not found in ' + self.config_file)

  def get(self, section, key, default_value=None):
    """
    Returns the value for the given section key pair

    """
    section = self.get_section(section)
    if key in section.keys():
      return section.get(key)
    elif default_value is None:
      raise ConfigKeyNotFoundException('Key ' + key + ' not found.')
    else:
      return default_value
