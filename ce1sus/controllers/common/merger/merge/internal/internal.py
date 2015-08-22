# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 11, 2015
"""
from ce1sus.controllers.common.merger.base import BaseMerger


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'

class Ce1susMerger(BaseMerger):

  def merge_attribute_definition(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'description', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'chksum', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'attributehandler_id', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'default_condition_id', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'regex', merge_cache))
      #table_id cannot change !!!
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'relation', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'value_type_id', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'share', merge_cache))

      # TODO: make also updates for the objects
      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_object_definition(self, old_instance, new_instance, merge_cache):

    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'description', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'chksum', merge_cache))
      #table_id cannot change !!!
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'default_share', merge_cache))

      # TODO: make also updates for the attributes
      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_reference_definition(self, old_instance, new_instance, merge_cache):


    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'regex', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'description', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'chksum', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'referencehandler_id', merge_cache))
      #table_id cannot change !!!
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'share', merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_condition(self, old_instance, new_instance, merge_cache):


    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'value', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'description', merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_mail_template(self, old_instance, new_instance, merge_cache):


    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'body', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'subject', merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_group(self, old_instance, new_instance, merge_cache):


    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'description', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'tlp_lvl', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'dbcode', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'default_dbcode', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'email', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'gpg_key', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'send_usermails', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'notifications', merge_cache))

      # TODO: merge children
      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_sync_server(self, old_instance, new_instance, merge_cache):


    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'user_id', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'baseurl', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'type_id', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'mode_code', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'description', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'certificate', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'ca_certificate', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'verify_ssl', merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_user(self, old_instance, new_instance, merge_cache):


    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'sirname', merge_cache))

      if new_instance.password:
        merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'password', merge_cache))

      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'email', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'api_key', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'gpg_key', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'dbcode', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'group_id', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'notifications', merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version


  def merge_attribute_type(self, old_instance, new_instance, merge_cache):


    if old_instance and new_instance:
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'name', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'description', merge_cache))
      merge_cache.version.add(self.update_instance_value(old_instance, new_instance, 'table_id', merge_cache))

      self.set_base(old_instance, new_instance, merge_cache)
    return merge_cache.version

  def merge_attribute(self, old_instance, new_instance, merge_cache):
    pass
