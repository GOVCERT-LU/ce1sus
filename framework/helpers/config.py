"""configuration module"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ConfigParser import ConfigParser, Error
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
    loggerClass = globals()['Log']
    function = getattr(loggerClass, 'getLogger')
    return function(self.__class__.__name__)
