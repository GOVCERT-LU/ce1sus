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
from dagr.db.session import SessionManager
import cherrypy


class Ce1susBaseController(BaseController):

  def __init__(self):
    BaseController.__init__(self)
    self.sessionManager = SessionManager.getInstance()
    self.userBroker = self.brokerFactory(UserBroker)

  def __internalCheck(self, event):
    result = False
    userDefaultGroup = Protector.getUserDefaultGroup()
    # if the user has no default group he has no rights
    if userDefaultGroup is None:
      raise cherrypy.HTTPError(403)
    user = Protector.getUser()

    # check if event is pubished valided and shared
    viewable = (event.published and
              event.bitValue.isValidated and
              event.bitValue.isSharable)
    # check if the event
    if viewable:
      if not result:
        # check tlp
        result = event.tlp.identifier >= userDefaultGroup.tlpLvl
        # check if the user belong to one of the common maingroups
        if not result:
          for group in event.maingroups:
            result = userDefaultGroup.identifier == group.identifier
            if result:
              break

        # check if the user belong to one of the common groups
        if not result:
          groups = Protector.getUserGroups()
          for group in event.groups:
            if group in groups:
                result = True
                break
    else:
      if not viewable:
        # check is the group of the user is the creation group
        result = event.creatorGroup.identifier == userDefaultGroup.identifier

    if not result:

      self.getLogger().debug("Event {0} is not viewable for user {1}".format(event.identifier,
                                                                  user.username
                                                                  ))
      raise cherrypy.HTTPError(403)

    self.getLogger().debug("Event {0} is viewable for user {1}".format(event.identifier,
                                                                  user.username
                                                                  ))
    return result

  def isAdminArea(self):
    attribute = getattr(cherrypy, 'session')
    return attribute.get('isAdminArea', False)

  def setAdminArea(self, value):
    attribute = getattr(cherrypy, 'session')
    attribute['isAdminArea'] = value

  def checkIfPriviledged(self):
    user = self.getUser()
    if not user.privileged:
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
    return self.sessionManager.brokerFactory(clazz)
