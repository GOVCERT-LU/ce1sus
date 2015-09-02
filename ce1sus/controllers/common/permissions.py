# -*- coding: utf-8 -*-

"""
(Description)

Created on Sep 2, 2015
"""
from ce1sus.common.utils import get_max_tlp, can_user_download
from ce1sus.controllers.base import BaseController, ControllerException
from ce1sus.db.brokers.event.eventbroker import EventBroker
from ce1sus.db.classes.internal.usrmgt.group import EventPermissions
from ce1sus.db.common.broker import BrokerException, NothingFoundException
from ce1sus.helpers.common.hash import hashSHA1


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2015, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class PermissionException(ControllerException):
  pass


class PermissionController(BaseController):

  def __init__(self, config, session=None):
    super(PermissionController, self).__init__(config, session)
    self.event_broker = self.broker_factory(EventBroker)

  def is_user_priviledged(self, user):
    self.logger.debug('Checking if user {0} is privileged'.format(user.username))
    if user:
      return user.permissions.privileged
    return False
  
  def get_max_tlp(self, group):
    self.logger.debug('Getting max tlp for group {0}'.format(group.name))
    return get_max_tlp(group)

  def is_instance_owner(self, instance, cache_object):
    """
    Returns true if the event is created by the user
  
    :param event:
    :type event: Event
    :param cache_object:
    :type cache_object: CacheObject
  
    :returns: Boolean
    """
    key = self.__get_cache_identifier(instance, cache_object.user, 'owner')
    owner = cache_object.authorized_cache.get(key, False)
    if owner:
      return owner
    
    self.logger.debug('Checking instance {2} {0} is created by {1}'.format(instance.uuid, cache_object.user.group.name, instance.get_classname()))
    if instance and cache_object.user:
      if self.is_user_priviledged(cache_object.user):
        cache_object.authorized_cache[key] = True
        return True
      else:
        if cache_object.user.group.identifier == instance.creator_group_id:
          cache_object.authorized_cache[key] = True
          return True
        else:
          cache_object.authorized_cache[key] = False
          return False
    else:
      cache_object.authorized_cache[key] = False
      return False

  def is_instance_viewable(self, instance, cache_object):
    key = self.__get_cache_identifier(instance, cache_object.user, 'owner')
    viewable = cache_object.authorized_cache.get(key, False)
    if viewable:
      return viewable

    key = self.__get_cache_identifier(instance, cache_object.user, 'view')
    viewable = cache_object.authorized_cache.get(key, False)
    if viewable:
      return viewable

    self.logger.debug('Checking if instance {2} {0} is viewable by {1}'.format(instance.uuid, cache_object.user.group.name, instance.get_classname()))
    if self.is_instance_owner(instance, cache_object):
      return True
    
    if hasattr(instance, 'properties') and hasattr(instance, 'tlp_level_id'):
      if instance.properties.is_validated and instance.properties.is_shareable:
        # only the items are shown which are supposed to be shown
        result = not instance.properties.marked_for_deletion
        cache_object.authorized_cache[key] = result
        return result
      elif cache_object.event_permissions:
        # check if user can validate the object
        if not instance.properties.is_validated and cache_object.event_permissions.can_validate:
          cache_object.authorized_cache[key] = True
          return True
  
    #still no result checking as last the tlp lvls
    user_tlp = self.get_max_tlp(cache_object.user.group)
    if instance.tlp_level_id >= user_tlp:
      cache_object.authorized_cache[key] = True
      return True
      #if the user group is in some way associated to the event
    else:
      
      event = instance.root
      if event is None:
        event = instance

      grp_ids = list()
      for group in cache_object.user.group.children:
        grp_ids.append(group.identifier)
      grp_ids.append(cache_object.user.group_id)
      
      for eventgroup in event.groups:
        group = eventgroup.group
        if group.identifier in grp_ids:
          cache_object.authorized_cache[key] = True
          return True

    cache_object.authorized_cache[key] = False
    return False

  def can_user_update(self, instance, cache_object):
    self.logger.debug('Checking if instance {2} {0} can be modified by {1}'.format(instance.uuid, cache_object.user.group.name, instance.get_classname()))
    if self.is_instance_owner(instance, cache_object):
      return True
    elif self.is_user_priviledged(cache_object.user):
      return True
    else:
      if cache_object.event_permissions:
        return cache_object.event_permissions.can_modify
      else:
        return False

  def set_properties_according_to_permisssions(self, instance, cache_object):
    self.logger.debug('Setting permission to {0} {1} for user {2} permissions'.format(instance.get_classname(), instance.uuid, cache_object.user.username))
    
    if self.is_instance_owner(instance, cache_object):
      instance.properties.is_proposal = False
      # owners are directly validated
      # TODO:ADD auto validate feature
      instance.properties.is_validated = True
    else:
      instance.properties.is_proposal = True
  
    instance.properties.is_rest_instert = cache_object.rest_insert
    instance.properties.is_web_insert = not cache_object.rest_insert

  def can_user_download(self, event, user):
    self.logger.debug('Checking if user {0} can download'.format(user.username))
    return can_user_download(event, user)

  def get_event_permissions(self, event, cache_object):
    try:
      # check if they are not in cache
      key = self.__get_cache_identifier(event, cache_object.user, 'permissions')
      permissions = cache_object.authorized_cache.get(key, None)
      if permissions:
        return permissions
      #If the user is owning the event give all persmissions 
      if self.is_instance_owner(event, cache_object):
        permissions = EventPermissions('0')
        permissions.set_all()
        cache_object.authorized_cache[key] = permissions
        return permissions
      else:
        permissions = self.event_broker.get_event_group_permissions(event, cache_object.user.group)
        if hasattr(permissions, 'permissions'):
          permissions = permissions.permissions
          cache_object.authorized_cache[key] = permissions
          return permissions
    except NothingFoundException:
      permissions = EventPermissions('0')
      cache_object.authorized_cache[key] = permissions
      return permissions
    except BrokerException as error:
      self.logger.error(error)
      raise PermissionException(error)

  def is_allowed_to_perform(self, event, action, cache_object):
    self.logger.debug('Checking is user {0} is allowed to perfrom {1} on event {2}'.format(cache_object.user.username, action, event.uuid))
    permissions = self.get_event_user_permissions(event, cache_object)
    if permissions:
      result = getattr(permissions, action)
      # if the result is still not set throw an error
      if result is None:
        raise PermissionException(u'Unknown error occurred during event checks')
      else:
        return result
    else:
      return False

  def is_user_allowed_set_validate(self, event, old_instance, cache_object, json):
    if self.is_instance_owner(event, cache_object):
      return True
    else:
      properties = json.get('properties', None)
      if properties:
        validated = properties.get('validated', None)
        if validated is None:
          return True
        else:
          # validate is perhaps going to change
          if cache_object.event_permissions.can_validate:
            return True
          else:
            # if there are changes deny them
            if old_instance.properties.is_validated == validated:
              # no change
              return True
            else:
              self.logger.info(u'User {0} has no right to validate elements of event {1}'.format(cache_object.user.username, event.identifier))
              return False
      return True

  def is_allowed_set_share(self, event, old_instance, cache_object, json):
    if self.is_instance_owner(event, cache_object):
      return True
    else:
      properties = json.get('properties', None)
      if properties:
        shared = properties.get('shared', None)
        if shared is None:
          return True
        else:
          if old_instance.properties.is_shareable == shared:
            return True
          else:
            self.logger.info(u'User/group {0}/{1} has no right to share elements of event {2}'.format(cache_object.user.username, cache_object.user.group.name, event.identifier))
            return False
      return True

  def is_allowed_set_validate_and_shared(self, event, old_instance, cache_object, json):
    # TODO: Involve if user == partof the originator
    validate = self.is_user_allowed_set_validate(event, old_instance, cache_object, json)
    shared = self.is_user_allowed_set_validate(event, old_instance, cache_object, json)
    return validate and shared

  @staticmethod
  def get_view_message(result, event_id, username, permission):
    """
    Returns the message for loggin
  
    :param event_id: identifer of the event
    :type event_id: Integer
    :param username:
    :type username: String
    :param result:
    :type result: Boolean
    """
    if result:
      return 'User "{1}" can perform action "{2}" on event "{0}"'.format(event_id, username, permission)
    else:
      return 'User "{1}" is not allowed perform action "{2}" on event "{0}"'.format(event_id, username, permission)

  @staticmethod
  def get_item_view_message(result, event_id, item_id, username, permission):
    if result:
      return 'User "{1}" can perform action "{2}" on event "{0}" for item {3}'.format(event_id, username, permission, item_id)
    else:
      return 'User "{1}" is not allowed perform action "{2}" on event "{0}" for item {3}'.format(event_id, username, permission, item_id)
  
  
  def if_is_modifiable(self, event):
    self.check_allowed_to_perform(event, 'can_modify')
  

  
  def __get_cache_identifier(self, instance, user, suffix=None):
    key = '{0}{1}{2}{3}'.format(user.username, instance.get_classname(), instance.uuid, suffix)
    self.logger.debug(key)
    key = hashSHA1(key)
    return key
  



