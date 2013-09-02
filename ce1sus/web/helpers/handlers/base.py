from abc import abstractmethod
from framework.web.helpers.templates import MakoHandler
from framework.helpers.debug import Log
from framework.db.session import SessionManager

class HandlerException(Exception):
  def __init__(self, message):
    Exception.__init__(self, message)

class HandlerBase(object):

  def __init__(self):
    self.mako = MakoHandler.getInstance()
    self.logger = Log.getLogger(self.__class__.__name__)
    self.__sessionHandler = SessionManager.getInstance()

  @abstractmethod
  def populateAttributes(self, params, obj, definition, user):
    raise HandlerException('populateAttributes not defined for {0}'.format(self.__class__.__name__));

  @abstractmethod
  def render(self, enabled, attribute=None):
    raise HandlerException('render not defined for {0}'.format(self.__class__.__name__));

  @abstractmethod
  def convertToAttributeValue(self, value):
    raise HandlerException('convert not defined for {0}'.format(self.__class__.__name__));

  def getTemplate(self, name):
    """Returns the template

    :param name: The name of the template (can also be a path)
    :type name: String

    :returns: Template
    """
    return self.mako.getTemplate(name)

  def brokerFactory(self, clazz):
    """
    Instantiates a broker.

    Note: In short sets up the broker in a correct manner with all the
    required settings

    :param clazz: The BrokerClass to be instantiated
    :type clazz: Extension of brokerbase

    :returns: Instance of a broker
    """
    return self.__sessionHandler.brokerFactory(clazz)

  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Log.getLogger(self.__class__.__name__)