# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for controllers.

Created: Jul, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.web.helpers.templates import MakoHandler
from dagr.helpers.debug import Log
from dagr.db.session import SessionManager
from ce1sus.web.helpers.protection import Protector
from ce1sus.brokers.permissionbroker import UserBroker
from dagr.web.helpers.config import WebConfig
from dagr.db.broker import NothingFoundException, BrokerException
from dagr.helpers.ldaphandling import LDAPHandler

class BaseController:
  """This is the base class for controlles all controllers should extend this
  class"""
  def __init__(self):
    self.mako = MakoHandler.getInstance()
    self.logger = Log.getLogger(self.__class__.__name__)
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
    self.logger.debug('Create broker for {0}'.format(clazz))
    return SessionManager.brokerFactory(clazz)

  def getTemplate(self, name):
    """Returns the template

    :param name: The name of the template (can also be a path)
    :type name: String

    :returns: Template
    """
    return self.mako.getTemplate(name)

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
    userBroker = self.brokerFactory(UserBroker)
    user = userBroker.getUserByUserName(self.getUserName())
    self.getLogger().debug("Returned user")
    return user

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
    return Log.getLogger(self.__class__.__name__)

  def returnAjaxOK(self):
    """
    Returns the string of an ok for the javascript

    :returns: String
    """
    return '--OK--' + self.__class__.__name__

  def getConfigVariable(self, identifier):
    """
    Returns the variable of the configuration file

    :param identifier: The name of the desired configuration
    :type identifier: String

    :returns:
    """
    return self.config.get(identifier)
