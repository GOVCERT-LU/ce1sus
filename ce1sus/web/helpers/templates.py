
from ce1sus.helpers.config import Configuration
from tempfile import gettempdir
from mako.lookup import TemplateLookup

class MakoHandler(object):

  def __init__(self, configFile):
    
    config = Configuration(configFile,'Mako')
    
    templateRoot = config.get('templateroot')
    collectionSize = config.get('collectionsize')
    outputEncoding = config.get('outputencoding')
    self.__mylookup = TemplateLookup(directories=[templateRoot],
                              module_directory=gettempdir()+'/mako_modules', 
                              collection_size=collectionSize,
                              output_encoding=outputEncoding, 
                              encoding_errors='replace')
    
    MakoHandler.instance = self
    
  def getTemplate(self, templatename):
    return self.__mylookup.get_template(templatename)
  
  def renderTemplate(self, templatename, **kwargs):
    mytemplate = self.__mylookup.get_template(templatename)
    return mytemplate.render_unicode(**kwargs)
  
  @staticmethod
  def getInstance():
    if MakoHandler.instance == None:
      raise IndentationError('No MakoHandler present')
    return MakoHandler.instance
