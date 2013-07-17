from ce1sus.helpers.config import Configuration


class WebConfig(object):
  def __init__(self, configFile):
    WebConfig.instance = self
    
    self.__config = Configuration(configFile,'WebPage')
    
  @staticmethod
  def getInstance():
    if WebConfig.instance == None:
      raise IndentationError('No SessionManager present')
    return WebConfig.instance
  