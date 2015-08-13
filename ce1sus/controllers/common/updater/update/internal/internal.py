# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""
from ce1sus.controllers.common.updater.base import BaseUpdater
from ce1sus.db.classes.internal.backend.servers import SyncServer
from ce1sus.db.classes.internal.report import ReferenceDefinition
from ce1sus.db.classes.internal.usrmgt.group import Group, EventPermissions
from ce1sus.db.classes.internal.usrmgt.user import User


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susUpdater(BaseUpdater):

  def update_attribute_definition(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version

  def update_attribute_type(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version

  def update_mail_template(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version

  def update_object_definition(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version
  
  def update_reference_definition(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version

  def update_condition_definition(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version

  def update_user(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version

  def update_serversync(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version

  def update_group(self, old_instance, json, cache_object):
    new_instance = self.assember.assemble(json, old_instance.__class__, None, cache_object)
    version = self.merger.merge(new_instance, old_instance, cache_object)
    return version

  def assemble_group(self, json, user, owner=False, rest_insert=True):
    group = Group()
    self.set_base(group, json, user, True, dict(), rest_insert, owner)
    if json:
      group.name = json.get('name', None)
      group.description = json.get('description', None)
      group.email = json.get('email', None)
      group.gpg_key = json.get('gpg_key', None)
      group.tlp_lvl = json.get('tlp_lvl', 3)
      # permissions setting
      group.permissions = self.assemble_permissions(json.get('permissions', None))
      group.default_permissions = self.assemble_permissions(json.get('default_event_permissions', None))
      group.notifications = json.get('notifications', None)

  def assemble_permissions(self, json):
    permissions = EventPermissions()
    if json:
      permissions.can_add = json.get('add', False)
      permissions.can_modify = json.get('modify', False)
      permissions.can_validate = json.get('validate', False)
      permissions.can_propose = json.get('propose', False)
      permissions.can_delete = json.get('delete', False)
      permissions.set_groups = json.get('set_groups', False)
    return permissions



  def assemble_reference_definition(self, json):
    ref_def = ReferenceDefinition()
    self.set_base(ref_def, json, None, True, dict(), True, True)
    return self.update_reference_definition(ref_def, json)

  def assemble_user(self, json):
    user = User()
    self.set_base(user, json, None, True, dict(), True, True)
    return self.update_user(user, json)

  def assemble_serversync(self, json, user, seen_groups=None, rest_insert=True, owner=True):
    if seen_groups is None:
      seen_groups = dict()

    server = SyncServer()
    self.set_base(server, json, user, True, seen_groups, rest_insert, owner)
    user_uuid = json.get('user_id', None)
    if not user_uuid:
      user = json.get('user', None)
      user_uuid = user.get('identifier', None)
    if user_uuid:
      user = self.user_broker.get_by_uuid(user_uuid)
      server.user = user
      server.user_id = user.identifier
    return server
