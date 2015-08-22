# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from difflib import SequenceMatcher

from ce1sus.common.checks import can_user_update, is_instance_owner, set_properties_according_to_permisssions
from ce1sus.controllers.base import BaseController
from ce1sus.db.classes.cstix.base import BaseCoreComponent
from ce1sus.db.classes.internal.core import SimpleLogingInformations, BaseElement
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class MergerException(Exception):
  pass 

class BaseMerger(BaseController):
  
  def __merge_properties(self, old_instance, new_instance, merger_cache):

    self.update_instance_value(old_instance, new_instance, 'is_validated', merger_cache, set_changes=False)
    self.update_instance_value(old_instance, new_instance, 'is_shareable', merger_cache, set_changes=False)
    self.update_instance_value(old_instance, new_instance, 'is_proposal', merger_cache, set_changes=False)
    self.update_instance_value(old_instance, new_instance, 'marked_for_deletion', merger_cache, set_changes=False)

    set_properties_according_to_permisssions(old_instance, merger_cache)

  def set_base(self, old_instance, new_instance, merge_cache):
    if isinstance(old_instance, SimpleLogingInformations):
      if merge_cache.object_changes:
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
          if isinstance(parent, SimpleLogingInformations):
            self.merge_simple_logging_informations(parent, old_instance, merge_cache)
          if hasattr(parent, 'version') and hasattr(new_instance, 'version'):
            self.set_version(parent, new_instance, merge_cache)
          if hasattr(parent, 'version') and not hasattr(new_instance, 'version'):
            if merge_cache.object_changes:
              super(BaseMerger, self).set_version(parent, merge_cache)
          self.update_modified(parent, new_instance, merge_cache)

  def set_version(self, old_instance, new_instance, merge_cache):
    if old_instance.version.compare(new_instance.version) > 0:
      self.changelogger.info('{0} {1} property version will be be replaced "{2}" by "{3}"'.format(old_instance.get_classname(), old_instance.uuid, old_instance.version.version, new_instance.version.version))
      old_instance.version.version = new_instance.version.version
    else:
      if merge_cache.object_changes:
        super(BaseMerger, self).set_version(old_instance, merge_cache)

  def is_updatable(self, old_instance, new_instance):
    if old_instance.get_classname() != new_instance.get_classname():
      raise MergerException('Cannot merge {0} and {1} both need to be the same class'.format(old_instance.get_classname(), new_instance.get_classname()))
    else:
      if isinstance(old_instance, SimpleLogingInformations):
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

  def update_instance_value(self, old_instance, new_instance, attr_name, merger_cache, set_changes=True):

    if old_instance and new_instance:
      if can_user_update(old_instance, merger_cache):
        if self.is_updatable(old_instance, new_instance):
          old_value = getattr(old_instance, attr_name)
          new_value = getattr(new_instance, attr_name)
          if new_value == '':
            new_value = None
          if old_value != new_value:
            self.changelogger.info('{0} {1} property {2} will be be replaced "{3}" by "{4}"'.format(old_instance.get_classname(), old_instance.uuid, attr_name, old_value, new_value))
            setattr(old_instance, attr_name, new_value)
            merger_cache.version = self.__detect_change_version(old_value, new_value)
            if set_changes:
              merger_cache.object_changes = True
        else:
          self.changelogger.info('{0} {1} property {2} will not be updated the existing one is newer'.format(old_instance.get_classname(), old_instance.uuid, attr_name))
      else:
        self.changelogger.warning('User {0} tried to update {1} {2} but does not have the permissions for it'.format(merger_cache.user.username, old_instance.get_classname(), old_instance.uuid))
    return merger_cache.version

  def __detect_change_version(self, old_value, new_value):
    version = Version()
    old_value = u'{0}'.format(old_value)
    new_value = u'{0}'.format(new_value)
    ratio = SequenceMatcher(None, old_value, new_value).ratio()
    if ratio == 1:
      pass
    elif ratio <= 0.50:
      version.increase_major()
    elif ratio <= 0.75:
      version.increase_minor()
    else:
      version.increase_patch()
    return version

  def is_instance_owner(self, instance, user, owner):
    if owner:
      return True
    else:
      return is_instance_owner(instance, user)

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
          return 1
      else:
        # delete
        if not merge_cache.owner:
          self.mark_for_deletion(old_instance, merge_cache)

    else:

      if new_instance:
        #add
        if not merge_cache.owner:
          self.mark_for_proposal(new_instance, merge_cache)
        return 0
    self.logger.debug('{0} is uptodate. old modified on is {1} and new one is {2}'.format(old_instance.get_classname(), old_instance.modified_on, new_instance.modified_on))
    return -1

  def merge_structured_text(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'id_', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'value', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'structuring_format', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'ordinality', merge_cache))

      elif result == 0:

        old_instance = new_instance

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_information_source(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'id_', merge_cache))
        merge_cache.version.add(self.merge_structured_text(new_instance.description, old_instance.description, merge_cache))
        merge_cache.version.add(self.merge_identity(new_instance.identity, old_instance.identity, merge_cache))
        merge_cache.version.add(self.merge_cybox_time(new_instance.time, old_instance.time, merge_cache))
        merge_cache.version.add(self.merge_tools(new_instance.tools, old_instance.tools, merge_cache))
        merge_cache.version.add(self.merge_roles(new_instance.roles, old_instance.roles, merge_cache))
        self.set_base(old_instance, new_instance, merge_cache)
      elif result == 0:
        merge_cache.version.add(Version().increase_major()())
        old_instance = new_instance

      self.set_base(old_instance, new_instance, merge_cache)
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

  def merge_gen_arrays(self, old_instance, new_instance, merge_cache, merge_fct):

    if len(new_instance) > 0 or len(old_instance) > 0:
      dict1 = self.__make_dict(old_instance)
      dict2 = self.__make_dict(new_instance)

      deleted_items = False
      added_items = False
      parent = None
      for key, old_item in dict1.iteritems():
        new_item = dict2.get(key, None)
        if parent is None:
          # it can only be one :P
          parent = old_item.parent
        if new_item:
          merge_cache.version.add(merge_fct(old_item, new_item, merge_cache))

          self.set_base(old_item, new_item, merge_cache)

          del(dict2[key])
        else:
          deleted_items = True
          self.mark_for_deletion(old_item, merge_cache)

      for item in dict2.itervalues():
        added_items = True
        old_instance.append(item)
        self.set_base(parent, None, merge_cache)


      # inc version as there are more changes
      if added_items or deleted_items:
        merge_cache.version.increase_minor()

    return merge_cache.version

  def merge_role(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'role_id', merge_cache))

      elif result == 0:
        merge_cache.version.add(Version().increase_major()())
        old_instance = new_instance



      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_roles(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_role)

  def merge_tools(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_tool)

  def merge_tool(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'id_', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'idref', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
        merge_cache.version.add(self.merge_structured_text(new_instance.description, old_instance.description, merge_cache))
        merge_cache.version.add(self.merge_structured_text(new_instance.short_description, old_instance.short_description, merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'vendor', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'version_db', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'service_pack', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'title', merge_cache))

      elif result == 0:
        old_instance = new_instance

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_identity(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'idref', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      elif result == 0:
        merge_cache.version.add(Version().increase_major()())
        old_instance = new_instance
      # TODO: merge related identities

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_cybox_time(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.merge_datetime_with_persision(new_instance.start_time, old_instance.start_time, merge_cache))
        merge_cache.version.add(self.merge_datetime_with_persision(new_instance.end_time, old_instance.end_time, merge_cache))
        merge_cache.version.add(self.merge_datetime_with_persision(new_instance.produced_time, old_instance.produced_time, merge_cache))
        merge_cache.version.add(self.merge_datetime_with_persision(new_instance.received_time, old_instance.received_time, merge_cache))
      elif result == 0:
        merge_cache.version.add(Version().increase_major()())
        old_instance = new_instance



      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_datetime_with_persision(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'value', merge_cache))
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'precision', merge_cache))
      elif result == 0:
        merge_cache.version.add(Version().increase_major()())
        old_instance = new_instance

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_package_intents(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_package_intent)

  def merge_package_intent(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'intent_id', merge_cache))
      elif result == 0:
        merge_cache.version.add(Version().increase_major()())
        old_instance = new_instance

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_handling(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_markingspecification)

  def merge_markingspecification(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      result = self.is_mergeable(old_instance, new_instance, merge_cache)
      if result == 1:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'id_', merge_cache))

        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'controlled_structure', merge_cache))
        merge_cache.version.add(self.merge_information_source(new_instance.information_source, old_instance.information_source, merge_cache))
        merge_cache.version.add(self.merge_markingstructures(new_instance.marking_structures, old_instance.marking_structures, merge_cache))
  
      elif result == 0:
        old_instance = new_instance

      self.set_version(old_instance, new_instance, merge_cache)
      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_markingstructures(self, old_instance, new_instance, merge_cache):
    return self.merge_gen_arrays(old_instance, new_instance, merge_cache, self.merge_markingspecification)

  def merge_markingstructure(self, old_instance, new_instance, merge_cache):
    # TODO: Marking Structures
    return Version()
