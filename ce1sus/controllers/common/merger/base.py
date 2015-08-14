# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 7, 2015
"""
from difflib import SequenceMatcher

from ce1sus.common.checks import can_user_update, is_instance_owner
from ce1sus.controllers.common.basechanger import BaseChanger, BaseChangerException
from ce1sus.db.classes.internal.core import SimpleLogingInformations, BaseElement
from ce1sus.helpers.changelogger import ChangeLogger
from ce1sus.helpers.version import Version


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class MergerException(BaseChangerException):
  pass 

class BaseMerger(BaseChanger):

  def __init__(self, config, session=None):
    super(BaseMerger, self).__init__(config, session)
    self.changelogger = ChangeLogger(config)

  def __merge_properties(self, old_instance, new_instance, cache_object):
    version = Version('0.0.0')
    version.add(self.update_instance_value(old_instance, new_instance, 'is_validated', cache_object))
    version.add(self.update_instance_value(old_instance, new_instance, 'is_shareable', cache_object))
    version.add(self.update_instance_value(old_instance, new_instance, 'is_proposal', cache_object))
    version.add(self.update_instance_value(old_instance, new_instance, 'marked_for_deletion', cache_object))

    self.set_properties_according_to_permisssions(old_instance, cache_object)

    return version

  def set_base(self, old_instance, new_instance, cache_object):
    super(BaseMerger, self).set_base(old_instance, None, cache_object, None)
    version = Version('0.0.0')
    if isinstance(old_instance, BaseElement):
      # merge properties
      if new_instance:
        version.add(self.__merge_properties(old_instance.properties, new_instance.properties, cache_object))

    return version



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

  def update_instance_value(self, old_instance, new_instance, attr_name, cache_object):
    version = Version('0.0.0')
    if can_user_update(old_instance, cache_object.user, cache_object.event_permissions):
      if self.is_updatable(old_instance, new_instance):
        old_value = getattr(old_instance, attr_name)
        new_value = getattr(new_instance, attr_name)
        if new_value == '':
          new_value = None
        if old_value != new_value:
          self.changelogger.info('{0} {1} property {2} will be be replaced "{3}" by "{4}"'.format(old_instance.get_classname(), old_instance.uuid, attr_name, old_value, new_value))
          setattr(old_instance, attr_name, new_value)
          version = self.__detect_change_version(old_value, new_value)
      else:
        self.changelogger.info('{0} {1} property {2} will not be updated the existing one is newer'.format(old_instance.get_classname(), old_instance.uuid, attr_name))
    else:
      self.changelogger.warning('User {0} tried to update {1} {2} but does not have the permissions for it'.format(cache_object.user.username, old_instance.get_classname(), old_instance.uuid))
    return version

  def __detect_change_version(self, old_value, new_value):
    version = Version('0.0.0')
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

  def is_mergeable(self, old_instance, new_instance, cache_object):
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
        if not cache_object.owner:
          self.mark_for_deletion(old_instance, cache_object)

    else:

      if new_instance:
        #add
        if not cache_object.owner:
          self.mark_for_proposal(new_instance, cache_object)
        return 0

    return -1

  def merge_structured_text(self, new_instance, old_instance, cache_object):
    version = Version()
    if new_instance and new_instance.value:
      result = self.is_mergeable(old_instance, new_instance, cache_object)
      if result == 1:
        version.add(self.update_instance_value(old_instance, new_instance, 'id_', cache_object))
        version.add(self.update_instance_value(old_instance, new_instance, 'value', cache_object))
        version.add(self.update_instance_value(old_instance, new_instance, 'structuring_format', cache_object))
        version.add(self.update_instance_value(old_instance, new_instance, 'ordinality', cache_object))
        self.set_base(old_instance, new_instance, cache_object)

      elif result == 0:
        version.add(Version().increase_major())
        old_instance = new_instance

    return version

  def merge_information_source(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'id_', cache_object))
      version.add(self.merge_structured_text(new_instance.description, old_instance.description, cache_object))
      version.add(self.merge_identity(new_instance.identity, old_instance.identity, cache_object))
      version.add(self.merge_cybox_time(new_instance.time, old_instance.time, cache_object))
      version.add(self.merge_tools(new_instance.tools, old_instance.tools, cache_object))
      version.add(self.merge_roles(new_instance.roles, old_instance.roles, cache_object))
      self.set_base(old_instance, new_instance, cache_object)
    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance


    return version

  def __make_dict(self, array):
    result = dict()
    for item in array:
      result[item.identifier] = item
    return result

  def mark_for_deletion(self, old_item, cache_object):
    # TODO: mark for deletion
    if not cache_object.owner:
      old_item.properties.marked_for_deletion

  def mark_for_proposal(self, new_item, cache_object):
    # TODO: mark for deletion
    if not cache_object.owner:
      new_item.properties.is_proposal

  def merge_gen_arrays(self, new_instance, old_instance, cache_object, merge_fct):
    version = Version()
    dict1 = self.__make_dict(old_instance)
    dict2 = self.__make_dict(new_instance)

    deleted_items = False
    added_items = False
    for key, old_item in dict1.iteritems():
      new_item = dict2.get(key, None)
      if new_item:
        version.add(merge_fct(new_item, old_item, cache_object))
        del(dict2[key])
      else:
        deleted_items = True
        self.mark_for_deletion(old_item)

    for item in dict2.itervalues():
      added_items = True
      old_instance.append(item)



    # inc version as there are more changes
    if added_items or deleted_items:
      version.increase_minor()

    self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_role(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'role_id', cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance


    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_roles(self, new_instance, old_instance, cache_object):
    return self.merge_gen_arrays(new_instance, old_instance, cache_object, self.merge_role)

  def merge_tools(self, new_instance, old_instance, cache_object):
    return self.merge_gen_arrays(new_instance, old_instance, cache_object, self.merge_tool)

  def merge_tool(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'id_', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'idref', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
      version.add(self.merge_structured_text(new_instance.description, old_instance.description, cache_object))
      version.add(self.merge_structured_text(new_instance.short_description, old_instance.short_description, cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'vendor', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'version_db', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'service_pack', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'title', cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance
      

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_identity(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'idref', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance
    # TODO: merge related identities


    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_cybox_time(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.merge_datetime_with_persision(new_instance.start_time, old_instance.start_time, cache_object))
      version.add(self.merge_datetime_with_persision(new_instance.end_time, old_instance.end_time, cache_object))
      version.add(self.merge_datetime_with_persision(new_instance.produced_time, old_instance.produced_time, cache_object))
      version.add(self.merge_datetime_with_persision(new_instance.received_time, old_instance.received_time, cache_object))
    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance
      

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_datetime_with_persision(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'value', cache_object))
      version.add(self.update_instance_value(old_instance, new_instance, 'precision', cache_object))
    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance


    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_package_intents(self, new_instance, old_instance, cache_object):
    return self.merge_gen_arrays(new_instance, old_instance, cache_object, self.merge_package_intent)

  def merge_package_intent(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'intent_id', cache_object))
    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance
      
    

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def merge_handling(self, new_instance, old_instance, cache_object):
    return self.merge_gen_arrays(new_instance, old_instance, cache_object, self.merge_markingspecification)

  def merge_markingspecification(self, new_instance, old_instance, cache_object):
    version = Version()
    result = self.is_mergeable(old_instance, new_instance, cache_object)
    if result == 1:
      version.add(self.update_instance_value(old_instance, new_instance, 'id_', cache_object))
  
      version.add(self.update_instance_value(old_instance, new_instance, 'controlled_structure', cache_object))
      version.add(self.merge_information_source(new_instance.information_source, old_instance.information_source, cache_object))
      version.add(self.merge_markingstructures(new_instance.marking_structures, old_instance.marking_structures, cache_object))

    elif result == 0:
      version.add(Version().increase_major()())
      old_instance = new_instance
      


    # set the new version
    if result == 1:
      old_instance.version.add(version)

    if self.is_change(version):
      self.set_base(old_instance, new_instance, cache_object)
    return version

  def is_change(self, version):
    if version.compare('0.0.0') < 0:
      return True
    return False

  def merge_markingstructures(self, new_instance, old_instance, cache_object):
    return self.merge_gen_arrays(new_instance, old_instance, cache_object, self.merge_markingspecification)

  def merge_markingstructure(self, new_instance, old_instance, cache_object):
    # TODO: Marking Structures
    return Version()
