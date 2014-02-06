# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for ce1sus controllers.

Created: 30 Sept, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

from dagr.controllers.base import BaseController
from ce1sus.brokers.permission.userbroker import UserBroker
from dagr.db.session import SessionManager
import cherrypy
from ce1sus.common.checks import check_if_event_is_viewable, check_viewable_message
from dagr.helpers.config import ConfigException
from dagr.controllers.base import ControllerException


class ControllerNothingFoundException(ControllerException):
  """Raised when nothing can be found"""
  pass


class Ce1susBaseController(BaseController):
  """
  Base for ce1sus controllers
  """
  def __init__(self, config):
    BaseController.__init__(self, config)
    self.session_manager = SessionManager(config)
    self.user_broker = self.broker_factory(UserBroker)

  def _get_user(self, username):
    return self.user_broker.getUserByUserName(username)

  def _raise_nothing_found_exception(self, error):
    """
    raises and logs an exception
    """
    self._get_logger().error(error)
    raise ControllerNothingFoundException(error)

  def _get_config_variable(self, key, default_value=None):
    """
    Returns the value of the configuration by key
    """
    try:
      return self.config.get('ce1sus', key, default_value)
    except ConfigException as error:
      self._raise_exception(error)

  def _is_event_viewable_for_user(self, event, user, cache):
    """
    check if the event can be seen by the user
    :param event:
    :type event: Event
    :param user:
    :type user: User

    :returns: Boolean
    """
    viewable = check_if_event_is_viewable(event, user, cache)
    log_msg = check_viewable_message(viewable, event.identifier, user.username)
    self._get_logger().info(log_msg)
    return viewable

  def isAdminArea(self):
    attribute = getattr(cherrypy, 'session')
    return attribute.get('isAdminArea', False)

  def set_admin_area(self, value):
    attribute = getattr(cherrypy, 'session')
    attribute['isAdminArea'] = value

  def checkIfPriviledged(self, user):
    if not user.privileged:
      raise cherrypy.HTTPError(403)

  def checkIfViewable(self, event, user, useCache=True):
    """
    Checks if the page if viewable for the given group

    :param grous: A list of strings contrianing the group names
    :type groups: list

    :returns: Boolean
    """
    # get eventfrom session
    if useCache:
      attribute = getattr(cherrypy, 'session')
      eventDict = attribute.get('ViewableEventsDict', None)
      if not eventDict:
        eventDict = attribute['ViewableEventsDict'] = dict()

      viewable = eventDict.get(event.identifier, None)
      if viewable == True:
        return True
      else:
        # set in session
        result = self.__internalCheck(event, user)
        attribute['ViewableEventsDict'][event.identifier] = result
        return result

    else:
      return self.__internalCheck(event, user)

  def getUserByAPIKey(self, apiKey):
    """
    Returns the api user

    :returns: User
    """
    if self.user_broker is None:
      self.user_broker = self.broker_factory(UserBroker)
    user = self.user_broker.getUserByApiKey(apiKey)
    self._get_logger().debug("Returned user")
    return user

  def getUserName(self):
    """
    Returns the session username

    :returns: String
    """
    self._get_logger().debug("Returned username")
    return Protector.getUserName()

  def clearSession(self):
    """
    Clears the session
    """
    self._get_logger().debug("Cleared session")
    Protector.clearSession()

  def is_event_owner(self, event, user):
    if user.privileged == 1:
      return True
    else:
      if user.group_id == event.creator_group_id:
        return True
      else:
        return False

  def broker_factory(self, clazz):
    """
    Instantiates a broker.

    Note: In short sets up the broker in a correct manner with all the
    required settings

    :param clazz: The BrokerClass to be instantiated
    :type clazz: Extension of brokerbase

    :returns: Instance of a broker
    """
    self._get_logger().debug('Create broker for {0}'.format(clazz))
    return self.session_manager.broker_factory(clazz)
