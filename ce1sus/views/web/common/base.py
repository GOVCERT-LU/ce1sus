# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 26, 2014
"""
import cherrypy

from ce1sus.common.checks import get_view_message, is_user_priviledged, is_event_owner, is_object_viewable, get_item_view_message
from ce1sus.controllers.events.event import EventController
from ce1sus.db.classes.group import EventPermissions
from ce1sus.db.classes.user import UserRights
from ce1sus.helpers.common.debug import Log
from ce1sus.helpers.common.objects import GenObject
from ce1sus.views.web.common.decorators import SESSION_KEY, SESSION_USER


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class BaseViewException(Exception):
  """
  Base exception for the view api
  """
  pass


class SessionNotFoundException(BaseViewException):
  """
  Not implemented exception
  """
  pass


class BaseView(object):

  def __init__(self, config):
    """
    Creator

    :param config: The configuration for this module
    :type config: Configuration

    :returns: BaseView
    """
    self.config = config
    self.__logger = Log(config)
    self.event_controller = EventController(config)

  @property
  def logger(self):
    return self.__logger.get_logger(self.__class__.__name__)

  def _create_session(self):
    """
    creates a session in cherrypy
    """
    session = self._get_session()
    session.regenerate()
    self.logger.debug('Created a session')

  def _put_to_session(self, key, value):
    """
      puts/sets a key value pair to the session

    :param key: The key for the value
    :type key: object
    :param value: The value for the key
    :type value: object

    """
    session = self._get_session()
    session[key] = value
    self.logger.debug('Set session value {0} for key {1}'.format(value, key))

  def __is_session_key(self, key):
    """
    Checks if the key is existing the session, else raises a SessionNotFoundException

    :param key: The key for the value
    :type key: object

    """
    session = self._get_session()
    if key not in session.keys():
      self.logger.debug('Key {0} is not defined in session'.format(key))
      raise SessionNotFoundException('Key {0} was not defined in session'.format(key))

  def _get_from_session(self, key, default_value=None):
    """
    Get a variable by key from the session

    Note: The variable stays in the session

    :param key: The key for the value
    :type key: object
    :param value: The value for the key
    :type value: object

    :returns: object
    """
    session = self._get_session()
    value = session.get(key, default_value)
    self.logger.debug('Returned session value "{0}" for key "{1}"'.format(value, key))
    return value

  def _pull_from_session(self, key, default_value=None):
    """
    Pulls a variable by key from the session

    Note: The variable is removed from the session

    :param key: The key for the value
    :type key: object
    :param value: The value for the key
    :type value: object

    :returns: object
    """
    session = self._get_session()
    value = session.pop(key, default_value)
    self.logger.debug('Returned session value "{0}" for key "{1}" and removed it'.format(value, key))
    return value

  def _destroy_session(self):
    """
    Destroys a session
    """
    try:
      session = self._get_session()
      session.clear()
      session.delete()
      # session.clean_up()
      self.logger.debug('Session destroyed')
    except:
      pass

  def _get_session(self):
    """
    Returns the session
    """
    session = getattr(cherrypy, 'session')
    self.logger.debug('Session returned')
    return session

  def user_authenticated(self):
    username = self._get_from_session(SESSION_KEY, None)
    return username

  def get_user(self):
    """
    Returns the user from the session

    :returns: User
    """
    user = self._get_from_session(SESSION_USER)
    return user

  def get_authorized_events_cache(self):
    """
    Returns the authorized cached events
    """
    try:
      return self._get_from_session('_cp_events_cache', dict())
    except AttributeError:
      return dict()

  def set_authorized_events_cache(self, cache):
    try:
      self._put_to_session('_cp_events_cache', cache)
    except AttributeError:
      pass

  def check_if_admin(self):
    user = self.get_user()
    isadmin = is_user_priviledged(user)
    if not isadmin:
      raise cherrypy.HTTPError(403, 'User {0} is not privileged'.format(user.username))

  def check_if_admin_validate(self):
    user = self.get_user()
    if not user.permissions.validate:
      raise cherrypy.HTTPError(403, 'User {0} cannot validate events'.format(user.username))

  def __get_max_tlp(self, user_group):
    if user_group.permissions.propagate_tlp:
      max_tlp = user_group.tlp_lvl
      for group in user_group.children:
        if group.tlp_lvl < max_tlp:
          max_tlp = group.tlp_lvl
        # check for group children
        child_max = self.__get_max_tlp(group)
        if child_max < max_tlp:
          max_tlp = child_max
      return max_tlp
    else:
      user_group.tlp_lvl

  def is_event_viewable(self, event, user=None):
    if not user:
      user = self.get_user()
    if event.originating_group_id == user.group_id:
      return True
    else:
      if user:
        if user.group_id:
          user_group = self.event_controller.group_broker.get_by_id(user.group_id)
          tlp_lvl = self.__get_max_tlp(user_group)
          if event.tlp_level_id >= tlp_lvl:
            return True
          else:
            grp_ids = list()
            for group in user_group.children:
              grp_ids.append(group.identifier)
            grp_ids.append(user.group_id)

            for eventgroup in event.groups:
              group = eventgroup.group
              if group.identifier in grp_ids:
                return True
            return False
        else:
          return False
      else:
        return False

  def check_if_event_is_viewable(self, event):
    user = self.get_user()
    if not self.is_event_viewable(event, user):
      raise cherrypy.HTTPError(403, 'User {0} cannot view this event'.format(user.username))

  def is_item_viewable(self, event, item, user=None):
    if not user:
      user = self.get_user()
    if self.is_event_owner(event, user):
      return True
    else:
      # check is the event is viewable then process to the iem
      if self.is_event_viewable(event, user):
        permissions = self.get_event_user_permissions(event, user)
        if is_object_viewable(item, permissions):
          return True
        else:
          # check if owner
          if item.creator_group_id == user.group.identifier:
            return True
          else:
            return False
      else:
        return False

  def check_item_is_viewable(self, event, item):
    user = self.get_user()
    result = self.is_item_viewable(event, item)
    # if the result is still not set throw an error
    log_msg = get_item_view_message(result, event.identifier, item.identifier, user.username, 'can_view')
    # update cache
    self.logger.info(log_msg)
    if result is None:
      raise Exception(u'Unknown error occurred during event checks')
    else:
      return result

  def check_if_event_is_modifiable(self, event):
    self.check_permission(event, 'can_modify')

  def check_if_event_is_deletable(self, event):
    self.check_permission(event, 'can_delete')

  def check_if_event_group_can_change(self, event):
    self.check_permission(event, 'set_groups')

  def check_permission(self, event, permission):
    user = self.get_user()
    result = self.is_user_allowed_to_perform(event, permission, user)
    if not result:
      raise cherrypy.HTTPError(403, 'User {0} is not authorized perform action "{2}" on event {1}'.format(user.username, event.identifier, permission))

  def check_if_owner(self, event):
    user = self.get_user()
    owner = is_event_owner(event, user)
    if not owner:
      raise cherrypy.HTTPError(403, 'User {0} is not owner of event {1}'.format(user.username, event.identifier))

  def check_if_user_can_add(self, event):
    user = self.get_user()
    result = is_event_owner(event, user)
    if not result:
      result = self.is_user_allowed_to_perform(event, 'can_add', user)
      if not result:
        result = self.is_user_allowed_to_perform(event, 'can_propose', user)
    if not result:
      raise cherrypy.HTTPError(403, 'User {0} can not add contents to event {1}'.format(user.username, event.identifier))

  def is_user_allowed_to_perform(self, event, permission, user):
    permissions = self.get_event_user_permissions(event, user)
    if permissions:
      result = getattr(permissions, permission)
      # if the result is still not set throw an error
      log_msg = get_view_message(result, event.identifier, user.username, permission)
      # update cache
      self.logger.info(log_msg)
      if result is None:
        raise Exception(u'Unknown error occurred during event checks')
      else:
        return result
    else:
      return False

  def is_user_priviledged(self, user):
    self.logger.debug(u'Checking if user {0} is privileged'.format(user.username))
    result = is_user_priviledged(user)
    if result:
      self.logger.info(u'User {0} is privileged'.format(user.username))
    else:
      self.logger.info(u'User {0} is not privileged'.format(user.username))
    return result

  def is_event_owner(self, event, user):
    self.logger.debug(u'Checking if user {0} is owner of event {1}'.format(user.username, event.identifier))
    result = is_event_owner(event, user)
    if result:
      self.logger.info(u'User {0} is owner of event {1}'.format(user.username, event.identifier))
    else:
      self.logger.info(u'User {0} is not owner of event {1}'.format(user.username, event.identifier))
    return result

  def is_rest_insert(self, headers):
    webinsert = headers.get('frontend', None)
    if webinsert:
      return False
    else:
      return True

  def is_user_allowed_set_validate(self, event, old_instance, user, json):
    properties = json.get('properties', None)
    if properties:
      permissions = self.get_event_user_permissions(event, user)
      validated = properties.get('validated', None)
      if validated is not None:
        # validate is perhaps going to change
        if permissions.can_validate:
          return True
        else:
          # if there are changes deny them
          if old_instance.properties.is_validated == validated:
            # no change
            return True
          else:
            self.logger.info(u'User {0} has no right to validate elements of event {1}'.format(user.username, event.identifier))
            return False
    return True

  def is_user_allowed_set_share(self, event, old_instance, user, json):
    properties = json.get('properties', None)
    if properties:
      shared = properties.get('shared', None)
      if shared is not None:
        if is_event_owner(event, user):
          return True
        else:
          if old_instance.originating_group.identifier == user.group_id:
            # User owns instance
            return True
          else:
            if old_instance.properties.is_shareable == shared:
              return True
            else:
              self.logger.info(u'User {0} has no right to share elements of event {1}'.format(user.username, event.identifier))
              return False
    return True

  def check_user_allowed_set_share(self, event, old_instance, user, json):
    shared = self.is_user_allowed_set_share(event, old_instance, user, json)
    if not shared:
      raise cherrypy.HTTPError(403, 'User {0} cannot make this change'.format(user.username))

  def check_user_allowed_set_validate(self, event, old_instance, user, json):
    validate = self.is_user_allowed_set_validate(event, old_instance, user, json)
    if not validate:
      raise cherrypy.HTTPError(403, 'User {0} can not validate elements of event {1}'.format(user.username, event.identifier))

  def is_if_user_can_set_validate_and_shared(self, event, old_instance, user, json):
    # TODO: Involve if user == partof the originator
    validate = self.is_user_allowed_set_validate(event, old_instance, user, json)
    shared = self.is_user_allowed_set_validate(event, old_instance, user, json)
    return validate and shared

  def check_if_user_can_set_validate_or_shared(self, event, old_instance, user, json):
    self.check_user_allowed_set_share(event, old_instance, user, json)
    self.check_user_allowed_set_validate(event, old_instance, user, json)

  def get_event_user_permissions(self, event, user):
    cache = self.get_authorized_events_cache()
    permissions = None
    if event:
      # check if cache
      if cache:
        permissions = cache.get(event.identifier, None)
        # if None the event is not available inside the cache
        if permissions:
          return permissions

      if permissions is None:
        if self.is_event_owner(event, user):
          permissions = EventPermissions('0')
          permissions.set_all()
        else:
          # either there was no cache or the event was not inside the cache perform checks
          permissions = self.event_controller.get_event_user_permissions(event, user)
          # put result in the cache if there is one
        cache[event.identifier] = permissions
        # perform checks
    else:
      permissions = EventPermissions('0')
    self.set_authorized_events_cache(cache)
    return permissions

  def put_user_to_session(self, user):
    cherrypy.request.login = user.username
    self._put_to_session('_cp_username', user.username)
    offline_user = self.__make_user_object(user)
    self._put_to_session(SESSION_USER, offline_user)

  def __make_user_object(self, user):
    # TODO: make user offline
    obj = GenObject()
    obj.name = user.name
    obj.username = user.username
    obj.identifier = user.identifier
    obj.email = user.email
    obj.group_id = user.group_id
    obj.activated = user.activated
    obj.sirname = user.sirname
    obj.permissions = UserRights(user.dbcode)

    return obj
