"""This module provides the base classes and interfaces
for controllers.
"""

from ce1sus.web.helpers.templates import MakoHandler
from ce1sus.helpers.debug import Logger
from ce1sus.db.session import SessionManager
from ce1sus.web.helpers.protection import Protector
from ce1sus.web.helpers.config import WebConfig



class BaseController:
  """This is the base class for controlles all controllers should extend this
  class"""
  def __init__(self):
    self.mako = MakoHandler.getInstance()
    self.logger = Logger.getLogger(self.__class__.__name__)
    self.__sessionHandler = SessionManager.getInstance()
    self.config = WebConfig.getInstance()

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

  def getTemplate(self, name):
    """Returns the template

    :param name: The name of the template (can also be a path)
    :type name: String

    :returns: Template
    """
    return self.mako.getTemplate(name)

  def checkCredentials(self, username=None, password=None):
    """
    Checks if the credentials are vaild

    :param username: The username
    :type username: String
    :param password: The password of the user in plain text?
    :typee password: String

    :returns: Boolean
    """
    self.getLogger().debug("Checked credentials for {0}".format(username))
    return Protector.checkCredentials(username, password)

  def checkIfViewable(self, groups, isOwner):
    """
    Checks if the page if viewable for the given group

    :param grous: A list of strings contrianing the group names
    :type groups: list

    :returns: Boolean
    """
    self.getLogger().debug("Checked if it is viewable for {0}".format(groups))
    return Protector.checkIfViewable(groups, isOwner)

  def getUser(self):
    """
    Returns the session user

    :returns: User
    """
    self.getLogger().debug("Returned user")
    return Protector.getUser()

  def getUserName(self):
    """
    Returns the session username

    :returns: String
    """
    self.getLogger().debug("Returned username")
    return Protector.getUserName()

  def clearSession(self):
    """
    Clears the session
    """
    self.getLogger().debug("Cleared session")
    Protector.clearSession()


  def getLogger(self):
    """
    Returns the logger

    :returns: Logger
    """
    return Logger.getLogger(self.__class__.__name__)
