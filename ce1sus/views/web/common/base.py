# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 26, 2014
"""
import cherrypy
from cherrypy._cperror import CherryPyException
from json import loads
from sqlalchemy.orm.session import make_transient
from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import BaseController
from ce1sus.controllers.events.event import EventController
from ce1sus.db.common.session import SessionManager
from ce1sus.helpers.common.debug import Log
from ce1sus.views.web.common.decorators import SESSION_KEY, SESSION_USER
from ce1sus.controllers.common.permissions import PermissionController


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

  controllers = dict()

  def __init__(self, config):
    """
    Creator

    :param config: The configuration for this module
    :type config: Configuration

    :returns: BaseView
    """
    self.config = config
    self.__logger = Log(self.config)
    self.session_manager = SessionManager(self.config)
    self.event_controller = self.controller_factory(EventController)
    self.user_controller = self.controller_factory(UserController)
    self.permission_controller = self.controller_factory(PermissionController)

  def controller_factory(self, clazz):
    if issubclass(clazz, BaseController):
      classname = clazz.__name__
      if classname in BaseView.controllers:
        return BaseView.controllers[classname]
      # need to create the broker
      self.logger.debug('Create controller for {0}'.format(clazz))
      instance = clazz(self.config)
      BaseView.controllers[classname] = instance
      return instance
    else:
      raise BaseViewException('Class does not implement BaseController')


  def get_json(self):
    json = {}
    cl = cherrypy.request.headers.get('Content-Length', None)
    if cl:
      try:
        rawbody = cherrypy.request.body.read(int(cl))
        json = loads(rawbody)
      except TypeError:
        # wonder what's wrong restangular?!?
        counter = 0
        rawbody = ''
        while True:
          rawbody += cherrypy.request.body.readline(counter)
          try:
            json = loads(rawbody)
            break
          except ValueError:
            counter += 1
    return json

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
    except CherryPyException as error:
      self.logger.error(error)

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

  def get_authorized_cache(self):
    """
    Returns the authorized cached events
    """
    try:
      return self._get_from_session('_cp_events_cache', dict())
    except AttributeError:
      return dict()

  def set_authorized_cache(self, cache):
    try:
      self._put_to_session('_cp_events_cache', cache)
    except AttributeError:
      pass

  def is_rest_insert(self, headers):
    webinsert = headers.get('frontend', None)
    if webinsert:
      return False
    else:
      return True

  def is_admin(self):
    user = self.get_user()
    isadmin = self.permission_controller.is_user_priviledged(user)
    return isadmin

  def check_if_admin(self):
    user = self.get_user()
    if not self.is_admin():
      raise cherrypy.HTTPError(403, 'User {0} is not privileged'.format(user.username))

  def check_if_admin_validate(self):
    user = self.get_user()
    if not user.permissions.validate:
      raise cherrypy.HTTPError(403, 'User {0} cannot validate events'.format(user.username))

  def is_instance_viewable(self, instance, cache_object):
    result = self.permission_controller.is_instance_viewable(instance, cache_object)
    self.set_authorized_cache(cache_object.authorized_cache)
    return result

  def check_if_instance_is_viewable(self, instance, cache_object):
    if not self.is_instance_viewable(instance, cache_object):
      raise cherrypy.HTTPError(403, 'User/group {0}/{1} cannot view this event'.format(cache_object.user.username, cache_object.user.group.name))

  def check_allowed_to_perform(self, event, action, cache_object):
    result = self.permission_controller.is_allowed_to_perform(event, action, cache_object)
    self.set_authorized_cache(cache_object.authorized_cache)
    if not result:
      raise cherrypy.HTTPError(403, 'User/group {0}/{1} is not authorized perform action "{3}" on event {2}'.format(cache_object.user.username, cache_object.user.group.name, event.uuid, action))

  def check_if_instance_owner(self, instance, cache_object):
    result = self.permission_controller.is_instance_owner(instance, cache_object)
    self.set_authorized_cache(cache_object.authorized_cache)
    if not result:
      raise cherrypy.HTTPError(403, 'User/group {0}/{1} does not own event {2}'.format(cache_object.user.username, cache_object.user.group.name, instance.uuid))

  def check_allowed_set_share(self, event, old_instance, cache_object, json):
    result = self.permission_controller.is_allowed_set_share(event, old_instance, cache_object, json)
    self.set_authorized_cache(cache_object.authorized_cache)
    if not result:
      raise cherrypy.HTTPError(403, 'User/group {0}/{1} cannot make this change'.format(cache_object.user.username, cache_object.user.group.name))

  def check_allowed_set_validate(self, event, old_instance, cache_object, json):
    result = self.permission_controller.is_user_allowed_set_validate(event, old_instance, cache_object, json)
    self.set_authorized_cache(cache_object.authorized_cache)
    if not result:
      raise cherrypy.HTTPError(403, 'User/group {0}/{1} can not validate elements of event {2}'.format(cache_object.user.username, cache_object.user.group.name, event.identifier))

  def check_if_is_modifiable(self, event, cache_object):
    self.check_allowed_to_perform(event, 'can_modify', cache_object)

  def check_if_is_deletable(self, event, cache_object):
    self.check_allowed_to_perform(event, 'can_delete', cache_object)

  def check_if_can_change_groups(self, event, cache_object):
    self.check_allowed_to_perform(event, 'set_groups', cache_object)

  def check_allowed_set_validate_or_shared(self, event, old_instance, cache_object, json):
    self.check_allowed_set_share(event, old_instance, cache_object, json)
    self.check_allowed_set_validate(event, old_instance, cache_object, json)

  def put_user_to_session(self, user):
    cherrypy.request.login = user.username
    self._put_to_session('_cp_username', user.username)
    offline_user = self.__make_user_object(user)
    self._put_to_session(SESSION_USER, offline_user)

  def __make_user_object(self, user):
    # TODO: make user offline
    for item in user.group.children:
      make_transient(item)
    make_transient(user.group)
    make_transient(user)

    return user
