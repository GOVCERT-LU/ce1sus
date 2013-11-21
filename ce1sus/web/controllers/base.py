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

  def __internalCheck(self, event):
    userDefaultGroup = Protector.getUserDefaultGroup()
    # if the user has no default group he has no rights
    if userDefaultGroup is None:
      raise cherrypy.HTTPError(403)
    user = Protector.getUser()
    self.getLogger().debug("Checked if it is viewable for user {0}".format(
                                                                  user.username
                                                                  )
                           )
    # check is the group of the user is the creation group
    result = event.creatorGroup.identifier == userDefaultGroup.identifier
    if not result:
      # check tlp
      result = event.tlp.identifier >= userDefaultGroup.tlpLvl
      # check if the user belong to one of the common maingroups
      if not result:
          result = userDefaultGroup in event.maingroups
      # check if the user belong to one of the common groups
      if not result:
        groups = Protector.getUserGroups()
        for group in event.groups:
          if group in groups:
              result = True
              break
    if not result:
      raise cherrypy.HTTPError(403)

    return result

  def checkIfOwner(self, event):
    if not self.isEventOwner(event):
      raise cherrypy.HTTPError(403)

  def checkIfViewable(self, event):
    """
    Checks if the page if viewable for the given group

    :param grous: A list of strings contrianing the group names
    :type groups: list

    :returns: Boolean
    """
    # get eventfrom session
    attribute = getattr(cherrypy, 'session')
    eventDict = attribute.get('ViewableEventsDict', None)
    if eventDict:
      viewable = eventDict.get(event.identifier, None)
      if viewable:
        return viewable
      else:
        # set in session
        self.getLogger().debug('Found rights in session')
        result = self.__internalCheck(event)
        attribute['ViewableEventsDict'][event.identifier] = result
        return result
    else:
      attribute['ViewableEventsDict'] = dict()
      # set in session
      result = self.__internalCheck(event)
      attribute['ViewableEventsDict'][event.identifier] = result
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

  def isEventOwner(self, event):
    user = Protector.getUser()
    if user.privileged == 1:
      return True
    else:
      if user.group_id == event.creatorGroup_id:
        return True
      else:
        return False
