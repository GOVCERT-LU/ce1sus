
__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from framework.helpers.config import Configuration

class WebConfig(object):

  instance = None
  def __init__(self, configFile):
    WebConfig.instance = self
    self.__config = Configuration(configFile, 'ce1sus')

  def get(self, identifier):
    return self.__config.get(identifier)


  @classmethod
  def getInstance(cls):
    if WebConfig.instance is None:
      raise IndentationError('No SessionManager present')
    return WebConfig.instance
