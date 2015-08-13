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

  def merge_attribtue_definition(self, new_instance, old_instance, cache_object):
    versions = list()
    versions.append(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'description', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'chksum', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'attributehandler_id', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'default_condition_id', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'regex', cache_object))
    #table_id cannot change !!!
    versions.append(self.update_instance_value(old_instance, new_instance, 'relation', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'value_type_id', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'share', cache_object))
    
    # TODO: make also updates for the objects
    self.set_base(old_instance, cache_object)
    return self.get_version(versions)

  def merge_object_definition(self, new_instance, old_instance, cache_object):
    versions = list()

    versions.append(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'description', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'chksum', cache_object))
    #table_id cannot change !!!
    versions.append(self.update_instance_value(old_instance, new_instance, 'default_share', cache_object))


    # TODO: make also updates for the attributes

    self.set_base(old_instance, new_instance, cache_object)
    return self.get_version(versions)

  def merge_reference_definition(self, new_instance, old_instance, cache_object):

    versions = list()

    versions.append(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'regex', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'description', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'chksum', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'referencehandler_id', cache_object))
    #table_id cannot change !!!
    versions.append(self.update_instance_value(old_instance, new_instance, 'share', cache_object))

    self.set_base(old_instance, new_instance, cache_object)
    return self.get_version(versions)

  def merge_condition(self, new_instance, old_instance, cache_object):

    versions = list()

    versions.append(self.update_instance_value(old_instance, new_instance, 'value', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'description', cache_object))

    self.set_base(old_instance, new_instance, cache_object)
    return self.get_version(versions)

  def merge_mail_template(self, new_instance, old_instance, cache_object):

    versions = list()

    versions.append(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'body', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'subject', cache_object))

    self.set_base(old_instance, new_instance, cache_object)
    return self.get_version(versions)

  def merge_group(self, new_instance, old_instance, cache_object):

    versions = list()

    versions.append(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'description', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'tlp_lvl', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'dbcode', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'default_dbcode', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'email', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'gpg_key', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'send_usermails', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'notifications', cache_object))

    # TODO: merge children

    self.set_base(old_instance, new_instance, cache_object)
    return self.get_version(versions)

  def merge_syncserver(self, new_instance, old_instance, cache_object):

    versions = list()

    versions.append(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'user_id', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'baseurl', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'type_id', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'mode_code', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'description', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'certificate', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'ca_certificate', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'verify_ssl', cache_object))

    self.set_base(old_instance, new_instance, cache_object)
    return self.get_version(versions)

  def merge_user(self, new_instance, old_instance, cache_object):

    versions = list()

    versions.append(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'sirname', cache_object))

    if new_instance.password:
      versions.append(self.update_instance_value(old_instance, new_instance, 'password', cache_object))

    versions.append(self.update_instance_value(old_instance, new_instance, 'email', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'api_key', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'gpg_key', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'dbcode', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'group_id', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'notifications', cache_object))

    self.set_base(old_instance, new_instance, cache_object)
    return self.get_version(versions)


  def merge_attribute_type(self, new_instance, old_instance, cache_object):

    versions = list()

    versions.append(self.update_instance_value(old_instance, new_instance, 'name', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'description', cache_object))
    versions.append(self.update_instance_value(old_instance, new_instance, 'table_id', cache_object))

    self.set_base(old_instance, new_instance, cache_object)
    return self.get_version(versions)
