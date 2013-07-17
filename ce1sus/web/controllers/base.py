from ce1sus.web.helpers.templates import MakoHandler
from ce1sus.helpers.debug import Logger
from ce1sus.db.session import SessionManager



class BaseController:
  
  def __init__(self):
    self.mako = MakoHandler.getInstance()
    self.logger = Logger.getLogger(self.__class__.__name__)
    self.__sessionHandler = SessionManager.getInstance()
    
  def brokerFactory(self,clazz):
    return self.__sessionHandler.brokerFactory(clazz)
  
  def log(self):
    return self.logger
  
  def renderPage(self, name, *args):
    template = self.mako.getTemplate(name)
    return template.render_unicode(*args)