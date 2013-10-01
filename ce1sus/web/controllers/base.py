# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for ce1sus controllers.

Created: 30 Sept, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from ce1sus.web.helpers.protection import Protector
from ce1sus.brokers.permissionbroker import UserBroker
from dagr.web.controllers.base import BaseController

class Ce1susBaseController(BaseController):

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
