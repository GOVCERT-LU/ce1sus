# -*- coding: utf-8 -*-

"""This module provides the base classes and interfaces
for ce1sus controllers.

Created: 30 Sept, 2013
"""

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

import cherrypy
from dagr.web.views.base import BaseView
from ce1sus.common.checks import check_if_event_is_viewable, check_viewable_message, is_event_owner


class Ce1susBaseView(BaseView):
  """
  Base class for ce1sus views
  """
  SESSION_USER = '_cp_user'

  def __init__(self, config):
    BaseView.__init__(self, config)

  def admin_area(self):
    """
    Returns if the admin area is set

    :returns: boolean
    """
    return self._get_from_session('isAdminArea', False)

  def set_admin_area(self, value):
    """
    Sets the admin area

    :param value: the value to set to
    :type value: boolean
    """
    self._put_to_session('isAdminArea', value)

  def _get_config_variable(self, key, default_value=None):
    """
    Returns the value of the configuration by key
    """
    return self.config.get('ce1sus', key, default_value)

  def _put_user_to_session(self, user):
    """
    Puts a fully populated user to the session

    :param user: The user
    :type user: User

    """
    self._put_to_session(Ce1susBaseView.SESSION_USER, user)

  def _get_user(self):
    """
    Returns the user from the session

    :returns: User
    """
    return self._get_from_session(Ce1susBaseView.SESSION_USER)

  def _get_authorized_events_cache(self):
    """
    Returns the authorized cached events
    """
    return self._get_from_session('_cp_events_cache', dict())

  def _check_if_event_is_viewable(self, event):
    """
    Checks if the user can view the event else raises an exception
    """
    user = self._get_user()
    cache = self._get_authorized_events_cache()
    viewable = check_if_event_is_viewable(event, user, cache)
    log_msg = check_viewable_message(viewable, event.identifier, user.username)
    self._get_logger().info(log_msg)

    if not viewable:
      raise cherrypy.HTTPError(403)

  def _check_if_event_owner(self, event):
    """
    Checks is the user is the event owner
    """
    valid = self._is_event_owner(event)
    if not valid:
      raise cherrypy.HTTPError(403)

  def _is_event_owner(self, event):
    """"
    Checks if the event is the owner

    :param event:
    :type event: Event

    :returns: Boolean
    """
    user = self._get_user()
    return is_event_owner(event, user)

  def _get_error_message(self, error):
    error_msg = '{0}'.format(error)
    self._get_logger().error(error)
    return error_msg

  def _render_error_page(self, error):
    """
    Renders an error dialog

    :param error: The error exception
    :type error: Exception

    :returns: generated HTML
    """
    return self._render_template('/common/error.html', error_msg=self._get_error_message(error))
