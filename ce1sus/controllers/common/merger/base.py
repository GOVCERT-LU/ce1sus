# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from difflib import SequenceMatcher

from ce1sus.controllers.base import BaseController
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.internal.core import SimpleLoggingInformations, BaseElement
from ce1sus.helpers.version import Version
from ce1sus.controllers.common.permissions import PermissionController


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class MergerException(Exception):
  pass 

class BaseMerger(BaseController):
  
  def __init__(self, config, session=None):
    super(BaseMerger, self).__init__(config, session)
    self.permission_controller = self.controller_factory(PermissionController)

  def __merge_properties(self, old_instance, new_instance, merger_cache):
    old_version = merger_cache.version.version
    self.update_instance_value(old_instance, new_instance, 'is_validated', merger_cache)
    self.update_instance_value(old_instance, new_instance, 'is_proposal', merger_cache)
    self.update_instance_value(old_instance, new_instance, 'marked_for_deletion', merger_cache)

    merger_cache.version.version = old_version

    # If items are visible or unvisible increase version
    self.update_instance_value(old_instance, new_instance, 'is_shareable', merger_cache)
    self.permission_controller.set_properties_according_to_permisssions(old_instance, merger_cache)

  def set_base(self, old_instance, new_instance, merge_cache):
    if isinstance(old_instance, SimpleLoggingInformations):
      self.merge_simple_logging_informations(old_instance, new_instance, merge_cache)

    if isinstance(old_instance, BaseElement):
      # merge properties
      if new_instance:
        # on
        self.__merge_properties(old_instance.properties, new_instance.properties, merge_cache)

    if isinstance(old_instance, BaseCoreComponent):
      self.set_version(old_instance, new_instance, merge_cache)
    # update parent informations
    self.update_modified(old_instance, new_instance, merge_cache)

  def update_modified(self, old_instance, new_instance, merge_cache):
    if old_instance:
      if hasattr(old_instance, 'parent'):
        parent = old_instance.parent
        if parent:
          if isinstance(parent, SimpleLoggingInformations):
            self.merge_simple_logging_informations(parent, new_instance, merge_cache, True)
          if hasattr(parent, 'version') and hasattr(new_instance, 'version'):
            self.set_version(parent, new_instance, merge_cache)
          elif hasattr(parent, 'version'):
            self.logger.debug('Setting {0}{1} adding {2} to version {3}'.format(parent.get_classname(), parent.uuid, merge_cache.version.version, parent.version.version))
            parent.version.add(merge_cache.version)
          self.update_modified(parent, new_instance, merge_cache)
      else:
        self.logger.debug('Has no parent')

  def set_version(self, old_instance, new_instance, merge_cache):
    """
    if merge_cache.is_changed_version(old_instance):
      self.logger.debug('Version already changed')
    else:
      merge_cache.set_changed_version(old_instance)
    """

    if isinstance(new_instance, BaseCoreComponent) and old_instance.version.compare(new_instance.version) > 0:
      self.logger.info('M {0} {1} property version will be be replaced "{2}" by "{3}" from instance'.format(old_instance.get_classname(), old_instance.uuid, old_instance.version.version, new_instance.version.version))
      old_instance.version.version = new_instance.version.version
    else:
      old_version = old_instance.version.version
      old_instance.version.add(merge_cache.version)
      self.logger.info('M {0} {1} property version will be be replaced "{2}" by "{3}" from cache'.format(old_instance.get_classname(), old_instance.uuid, old_version, old_instance.version.version))

  def is_updatable(self, old_instance, new_instance):
    if old_instance.get_classname() != new_instance.get_classname():
      raise MergerException('Cannot merge {0} and {1} both need to be the same class'.format(old_instance.get_classname(), new_instance.get_classname()))
    else:
      if isinstance(old_instance, SimpleLoggingInformations):
        if old_instance.modified_on < new_instance.modified_on:
          return True
        elif hasattr(old_instance, 'version'):
          # check if the version differs
          if old_instance.version.compare(new_instance.version):
            return True
          else:
            return False
        else:
          return False
      else:
        # always update if there are no logging informations
        return True

  def update_instance_value(self, old_instance, new_instance, attr_name, merger_cache):

    if old_instance and new_instance:
      if self.permission_controller.can_user_update(old_instance, merger_cache):
        if self.is_updatable(old_instance, new_instance):
          old_value = getattr(old_instance, attr_name)
          new_value = getattr(new_instance, attr_name)
          if new_value == '':
            new_value = None
          if old_value != new_value:
            self.changelogger.info('{0} {1} property {2} will be be replaced "{3}" by "{4}"'.format(old_instance.get_classname(), old_instance.uuid, attr_name, old_value, new_value))
            setattr(old_instance, attr_name, new_value)
            self.__detect_change_version(old_value, new_value, merger_cache)
        else:
          self.changelogger.info('{0} {1} property {2} will not be updated the existing one is newer'.format(old_instance.get_classname(), old_instance.uuid, attr_name))
      else:
        self.changelogger.warning('User {0} tried to update {1} {2} but does not have the permissions for it'.format(merger_cache.user.username, old_instance.get_classname(), old_instance.uuid))
    return merger_cache.version

  def __detect_change_version(self, old_value, new_value, merger_cache):
    old_value = u'{0}'.format(old_value)
    new_value = u'{0}'.format(new_value)
    ratio = SequenceMatcher(None, old_value, new_value).ratio()
    if ratio == 1:
      pass
    elif ratio <= 0.50:
      merger_cache.inc_version_major()
    elif ratio <= 0.75:
      merger_cache.inc_version_minior()
    else:
      merger_cache.inc_version_patch()

  def is_instance_owner(self, instance, user, owner):
    if owner:
      return True
    else:
      return self.permission_controller.is_instance_owner(instance, user)

  def is_mergeable(self, old_instance, new_instance, merge_cache):
    """
    Returns:
      1: can be merged
      0: must be added
      -1: do nothing
    """
    if old_instance:

      if new_instance:
        if old_instance.modified_on < new_instance.modified_on:
          self.logger.debug('{0} {1} will be updated.'.format(old_instance.get_classname(), old_instance.uuid, old_instance.modified_on))
          return 1
      else:
        # mark it for deletion if it is not the owner if it is not present anymore
        if not merge_cache.owner:
          self.mark_for_deletion(old_instance, merge_cache)
          self.logger.debug('{0} {1} is marked for deletion.'.format(old_instance.get_classname(), old_instance.uuid, old_instance.modified_on))

    else:

      if new_instance:
        #add
        if not merge_cache.owner:
          self.mark_for_proposal(new_instance, merge_cache)
          self.logger.debug('{0} is marked for proposal.'.format(new_instance.get_classname(), new_instance.modified_on))
        return 0
    self.logger.debug('{0} {1} is up to date.'.format(old_instance.get_classname(), old_instance.uuid, old_instance.modified_on))
    return -1

  def merge_structured_text(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      result = self.is_mergeable(old_value, new_value, merge_cache)
      if result == 1:
        self.update_instance_value(old_value, new_value, 'id_', merge_cache)
        self.update_instance_value(old_value, new_value, 'value', merge_cache)
        self.update_instance_value(old_value, new_value, 'structuring_format', merge_cache)
        self.update_instance_value(old_value, new_value, 'ordinality', merge_cache)
        self.set_base(old_value, new_value, merge_cache)

      elif result == 0:
        self.logger.info('Adding structured text with value {0}'.format(new_value.value))
        self.set_value(old_instance, new_value, attr_name, merge_cache)



    return merge_cache.version

  def merge_information_source(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      result = self.is_mergeable(old_value, new_value, merge_cache)
      if result == 1:
        self.update_instance_value(old_value, new_value, 'id_', merge_cache)
        self.set_base(old_value, new_value, merge_cache)
      elif result == 0:
        self.logger.info('Adding new information source')
        self.set_value(old_instance, new_value, attr_name, merge_cache)

      self.merge_structured_text(old_value, new_value, merge_cache, 'description')
      # self.merge_identity(old_value, new_value, merge_cache, 'identity')
      self.merge_cybox_time(old_value, new_value, merge_cache, 'time')
      self.merge_tools(old_value, new_value, merge_cache, 'tools')
      self.merge_roles(old_value, new_value, merge_cache, 'roles')

    return merge_cache.version

  def __make_dict(self, array):
    result = dict()
    for item in array:
      result[item.uuid] = item
    return result

  def mark_for_deletion(self, old_item, cache_object):
    # TODO: mark for deletion
    if not cache_object.owner:
      old_item.properties.marked_for_deletion

  def mark_for_proposal(self, new_item, cache_object):
    # TODO: mark for deletion
    if not cache_object.owner:
      new_item.properties.is_proposal

  def merge_gen_arrays(self, old_instance, new_instance, merge_cache, merge_fct, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)

    if new_value is None:
      # skip if new one has no list
      return merge_cache.version

    if old_value is None:
      setattr(old_instance, attr_name, list())

    if len(new_value) > 0 or len(old_value) > 0:
      dict1 = self.__make_dict(old_value)
      dict2 = self.__make_dict(new_value)

      parent = None
      for key, old_item in dict1.iteritems():
        new_item = dict2.get(key, None)
        if parent is None:
          # it can only be one :P
          parent = old_item.parent
        if new_item:
          merge_fct(old_item, new_item, merge_cache)

          del(dict2[key])
        else:
          self.mark_for_deletion(old_item, merge_cache)

      for item in dict2.itervalues():
        if old_value is None:
          setattr(old_instance, attr_name, list())
        old_value.append(item)
        merge_cache.inc_version_major()
        self.set_base(parent, None, merge_cache)

    return merge_cache.version

  def merge_role(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      result = self.is_mergeable(old_value, new_value, merge_cache)
      if result == 1:
        self.update_instance_value(old_value, new_value, 'role_id', merge_cache)
        self.set_base(old_value, new_value, merge_cache)
      elif result == 0:
        self.set_value(old_instance, new_value, attr_name)

    return merge_cache.version

  def merge_roles(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_role, attr_name)

  def merge_tools(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_tool, attr_name)

  def merge_tool(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      result = self.is_mergeable(old_value, new_value, merge_cache)
      if result == 1:
        self.update_instance_value(old_value, new_value, 'id_', merge_cache)
        self.update_instance_value(old_value, new_value, 'idref', merge_cache)
        self.update_instance_value(old_value, new_value, 'name', merge_cache)
        self.update_instance_value(old_value, new_value, 'vendor', merge_cache)
        self.update_instance_value(old_value, new_value, 'version_db', merge_cache)
        self.update_instance_value(old_value, new_value, 'service_pack', merge_cache)
        self.update_instance_value(old_value, new_value, 'title', merge_cache)
        self.set_base(old_value, new_value, merge_cache)

      elif result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)

      self.merge_structured_text(old_value, new_value, merge_cache, 'description')
      self.merge_structured_text(old_value, new_value, merge_cache, 'short_description')

    return merge_cache.version

  def merge_identity(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      result = self.is_mergeable(old_value, new_value, merge_cache)
      if result == 1:
        self.update_instance_value(old_value, new_value, 'idref', merge_cache)
        self.update_instance_value(old_value, new_value, 'name', merge_cache)
        self.set_base(old_value, new_value, merge_cache)
      elif result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)
      # TODO: merge related identities

    return merge_cache.version

  def merge_cybox_time(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      result = self.is_mergeable(old_value, new_value, merge_cache)

      if result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)

      self.merge_datetime_with_persision(old_value, new_value, merge_cache, 'start_time')
      self.merge_datetime_with_persision(old_value, new_value, merge_cache, 'end_time')
      self.merge_datetime_with_persision(old_value, new_value, merge_cache, 'produced_time')
      self.merge_datetime_with_persision(old_value, new_value, merge_cache, 'received_time')

    return merge_cache.version

  def merge_datetime_with_persision(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      result = self.is_mergeable(old_value, new_value, merge_cache)
      if result == 1:
        self.update_instance_value(old_value, new_value, 'value', merge_cache)
        self.update_instance_value(old_value, new_value, 'precision', merge_cache)
        self.set_base(old_value, new_value, merge_cache)

      elif result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)


    return merge_cache.version

  def merge_package_intents(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_package_intent, attr_name)

  def merge_package_intent(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_value:
      result = self.is_mergeable(old_value, new_value, merge_cache)
      if result == 1:
        self.update_instance_value(old_value, new_value, 'intent_id', merge_cache)
        self.set_base(old_value, new_value, merge_cache)
      elif result == 0:
        self.set_value(old_instance, new_value, attr_name, merge_cache)

    return merge_cache.version

  def merge_handling(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_markingspecification, attr_name)

  def merge_markingspecification(self, old_instance, new_instance, merge_cache, attr_name=None):
    old_value, new_value = self.get_values(old_instance, new_instance, attr_name)
    if old_value or new_instance:
      result = self.is_mergeable(old_value, new_value, merge_cache)
      if result == 1:
        self.update_instance_value(old_value, new_value, 'id_', merge_cache)

        self.update_instance_value(old_value, new_value, 'controlled_structure', merge_cache)
        self.set_version(old_value, new_value, merge_cache)
        self.set_base(old_value, new_value, merge_cache)

      elif result == 0:
        old_instance = new_instance

      self.merge_information_source(old_value, new_value, merge_cache, 'information_source')
      self.merge_markingstructures(old_value, new_value, merge_cache, 'marking_structures')

    return merge_cache.version

  def merge_markingstructures(self, old_instance, new_instance, merge_cache, attr_name=None):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_markingspecification, attr_name)

  def merge_markingstructure(self, old_instance, new_instance, merge_cache, attr_name=None):
    # TODO: Marking Structures
    return Version()

  def __get_value(self, instance, attr_name):
    if attr_name:
      if instance:
        value = getattr(instance, attr_name)
        return value
      else:
        return list()
    else:
      return instance


  def get_values(self, old_instance, new_instance, attr_name):
    # check if the classes are the same
    if old_instance and new_instance:
      if old_instance.get_classname() != new_instance.get_classname():
        raise MergerException('Class {0} is not the same as {1}'.format(old_instance.get_classname(), new_instance.get_classname()))
    
    return self.__get_value(old_instance, attr_name), self.__get_value(new_instance, attr_name)

      

  def set_value(self, old_instance, new_value, attr_name, merge_cache):
    if hasattr(new_value, 'parent'):
      new_value.parent = old_instance
    merge_cache.inc_version_major()
    setattr(old_instance, attr_name, new_value)
