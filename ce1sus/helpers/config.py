"""configuration module"""

from ConfigParser import ConfigParser
from os.path import isfile
from os import getcwd


class ConfigException(Exception):
  """Configuration Exception"""

  def __init__(self, message):
    Exception.__init__(self, message)



class Configuration(object):

  """Configuration class"""

  def __init__(self, configFile, section):
    self.configDict = dict()
    config = ConfigParser()
    if not isfile(configFile):
      raise ConfigException('Could not find config file ' +
                            configFile + ' in ' + getcwd())
    config.read(configFile)

    if config.has_section(section):
      options = config.options(section)
      for option in options:
        try:
          string = config.get(section, option)
          if string.upper() in ['YES', 'NO', 'TRUE', 'FALSE']:
            self.configDict[option] = config.getboolean(section, option)
          else:
            if string.isdigit():
              self.configDict[option] = config.getint(section, option)
            else:
              self.configDict[option] = string
        except Exception as e:
          self.getLogger().error(e)
          self.configDict[option] = None
    else:
      raise ConfigException('Section ' + section + ' is not found in ' +
                             configFile)

  def get(self, identifier):
    """
    Returns the value for the given identifier

    :returns: Any
    """
    try:
      return self.configDict[identifier]
    except KeyError:
      self.getLogger().error('Key ' + identifier + ' not found.')
      raise ConfigException('Key ' + identifier + ' not found.')

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Logger.getLogger(self.__class__.__name__)
