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
from dagr.web.controllers.base import BaseController
from ce1sus.brokers.permission.userbroker import UserBroker
import cherrypy


class Ce1susBaseController(BaseController):

  def __init__(self):
    BaseController.__init__(self)
    self.userBroker = self.brokerFactory(UserBroker)

  def checkIfViewable(self, event):
    """
    Checks if the page if viewable for the given group

    :param grous: A list of strings contrianing the group names
    :type groups: list

    :returns: Boolean
    """
    user = Protector.getUser()
    self.getLogger().debug("Checked if it is viewable for user {0}".format(
                                                                  user.username
                                                                  )
                           )
    result = event.creator.identifier == user.identifier
    if not result:
      # check tlp
      tlpLevel = 3
      groups = Protector.getUserGroups()
      if groups is None:
        return tlpLevel
      else:
        for group in groups:
          tlpLevel = min(tlpLevel, group.tlpLvl)
      result = event.tlp.identifier >= tlpLevel
      if not result:
        for userGrp in user.groups:
          for group in groups:
            if userGrp == group:
              result = True
              break
    if not result:
      raise cherrypy.HTTPError(403)

    return result

  def getUser(self, cached=False):
    """
    Returns the session user

    :returns: User
    """
    self.getLogger().debug("Returned user")
    if cached:
      return Protector.getUser()
    else:
      return self.userBroker.getUserByUserName(self.getUserName())

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
