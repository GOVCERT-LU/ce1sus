# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 4, 2015
"""
import re

from ce1sus.controllers.admin.attributedefinitions import gen_attr_chksum
from ce1sus.controllers.admin.objectdefinitions import gen_obj_chksum
from ce1sus.controllers.admin.references import gen_reference_chksum
from ce1sus.controllers.common.assembler.base import BaseAssembler, AssemblerException
from ce1sus.db.brokers.definitions.conditionbroker import ConditionBroker
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.brokers.definitions.referencesbroker import ReferencesBroker
from ce1sus.db.brokers.definitions.typebrokers import AttributeTypeBroker
from ce1sus.db.classes.internal.attributes.attribute import Condition
from ce1sus.db.classes.internal.backend.mailtemplate import MailTemplate
from ce1sus.db.classes.internal.backend.servers import SyncServer, ServerMode
from ce1sus.db.classes.internal.backend.types import AttributeType
from ce1sus.db.classes.internal.definitions import AttributeDefinition, ObjectDefinition
from ce1sus.db.classes.internal.report import ReferenceDefinition
from ce1sus.db.classes.internal.usrmgt.group import Group, EventPermissions
from ce1sus.db.classes.internal.usrmgt.user import User, UserRights
from ce1sus.db.common.broker import BrokerException, NothingFoundException
from ce1sus.helpers.common.hash import hashSHA1
from ce1sus.helpers.pluginfunctions import is_plugin_available, get_plugin_function


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


class Ce1susAssembler(BaseAssembler):

  def __init__(self, config, session=None):
    super(Ce1susAssembler, self).__init__(config, session)
    self.salt = self.config.get('ce1sus', 'salt', None)
    self.references_broker = self.broker_factory(ReferencesBroker)
    self.handler_broker = self.broker_factory(AttributeHandlerBroker)
    self.value_type_broker = self.broker_factory(AttributeTypeBroker)
    self.condition_broker = self.broker_factory(ConditionBroker)
    self.salt = self.config.get('ce1sus', 'salt', None)


  def assemble_group(self, json, cache_object):
    group = Group()
    self.set_base(group, json, cache_object, None)
    if json:
      group.name = json.get('name', None)
      group.description = json.get('description', None)
      group.email = json.get('email', None)
      group.gpg_key = json.get('gpg_key', None)
      group.tlp_lvl = json.get('tlp_lvl', 3)
      # permissions setting
      self.assemble_permissions(json.get('permissions', None), group, cache_object)
      self.assemble_permissions(json.get('default_event_permissions', None), group, cache_object, 'default_dbcode')
      group.notifications = json.get('notifications', None)
      return group

  def assemble_permissions(self, json, parent, cache_object, attr_name='dbcode'):
    permissions = EventPermissions('0', parent, attr_name)
    if json:
      permissions.can_add = json.get('add', False)
      permissions.can_modify = json.get('modify', False)
      permissions.can_validate = json.get('validate', False)
      permissions.can_propose = json.get('propose', False)
      permissions.can_delete = json.get('delete', False)
      permissions.set_groups = json.get('set_groups', False)
    return permissions

  def assemble_user_permissions(self, json, parent, cache_object):
    permissions = UserRights('0', parent)
    if json:
      permissions.privileged = json.get('priviledged', False)
      permissions.disabled = json.get('disabled', False)
      permissions.manage_group = json.get('manage_group', False)
      permissions.validate = json.get('validate', False)
      return permissions

  def assemble_attribute_definition(self, json, cache_object):
    if json:
      attr_def = AttributeDefinition()
      self.set_base(attr_def, json, cache_object, None)

      attr_def.name = json.get('name', None)
      attr_def.description = json.get('description', None)
      attr_def.relation = json.get('relation', False)
      attr_def.share = json.get('share', False)
      attr_def.regex = json.get('regex', None)
      attr_def.table_id = json.get('table_id', None)
      # The user cannot set this !!
      # attr_def.cybox_std = json.get('cybox_std', False)
      attr_def.cybox_std = False

      # The chksum is always computed
      attr_def.chksum = gen_attr_chksum(attr_def)
      """
      chksum = json.get('chksum', None)
      if chksum:
        attr_def.chksum = chksum
      else:
        attr_def.chksum = gen_attr_chksum(attr_def)
      """

      attributehandler_uuid = json.get('attributehandler_id', None)
      if attributehandler_uuid:
        attribute_handler = self.handler_broker.get_by_uuid(attributehandler_uuid)
        attr_def.attributehandler_id = attribute_handler.identifier
        attr_def.attribute_handler = attribute_handler
      else:
        raise AssemblerException('Attribute definition does not have a handler specified')

      value_type_uuid = json.get('type_id', None)
      if value_type_uuid:
        value_type = self.value_type_broker.get_by_uuid(value_type_uuid)
        attr_def.value_type_id = value_type.identifier
        attr_def.value_type = value_type
      else:
        raise AssemblerException('Attribute definition does not have a value type specified')

      default_condition_uuid = json.get('default_condition_id', None)
      if default_condition_uuid:
        default_condition = self.condition_broker.get_by_uuid(default_condition_uuid)
        attr_def.default_condition_id = default_condition.identifier
        attr_def.default_condition = default_condition
      else:
        raise AssemblerException('Attribute definition does not have a condition specified')

      # link attribute handler
      try:
        attribute_handler = self.handler_broker.get_by_uuid(attributehandler_uuid)
        attr_def.attributehandler_id = attribute_handler.identifier
        attr_def.attribute_handler = attribute_handler
      except BrokerException as error:
        raise AssertionError(error)

      return attr_def

  def assemble_reference_definition(self, json, cache_object):
    if json:
      ref_def = ReferenceDefinition()
      self.set_base(ref_def, json, cache_object, None)
      ref_def.name = json.get('name', None)
      ref_def.description = json.get('description', None)
      ref_def.share = json.get('share', False)
      ref_def.regex = json.get('regex', None)


      # The chksum is always computed
      ref_def.chksum = gen_reference_chksum(ref_def)
      """
      chksum = json.get('chksum', None)
      if chksum:
        ref_def.chksum = chksum
      else:
        ref_def.chksum = gen_reference_chksum(ref_def)
      """

      referencehandler_uuid = json.get('referencehandler_id', None)
      if referencehandler_uuid:
        try:
          referencehandler = self.references_broker.get_handler_by_uuid(referencehandler_uuid)
          ref_def.referencehandler_id = referencehandler.identifier
          ref_def.referencehandler = referencehandler
        except BrokerException as error:
          raise AssemblerException(error)
      else:
        raise AssemblerException('Reference definition does not have a handler specified')

      return ref_def

  def assemble_user(self, json, cache_object):
    if json:
      user = User()
      self.set_base(user, json, cache_object, None)
      user.name = json.get('name', None)
      user.email = json.get('email', None)
      user.gpg_key = json.get('gpg_key', None)
      user.api_key = json.get('api_key', None)
      user.sirname = json.get('sirname', None)
      user.username = json.get('username', None)
      plain_password = json.get('password', None)
      if plain_password != '*******************':
        # TODO: use variable
        user.plain_password = plain_password

      user.notifications = json.get('notifications', None)
      # permissions setting
      self.permissions = self.assemble_user_permissions(json.get('permissions', '0'), user, cache_object)
      if self.salt:
        salt = self.salt
      else:
        salt = user.username
      if user.plain_password:
        fistcheck = True
        if is_plugin_available('ldap', self.config):
          ldap_password_identifier = get_plugin_function('ldap', 'get_ldap_pwd_identifier', self.config, 'internal_plugin')()
          if user.plain_password == ldap_password_identifier:
            user.password = ldap_password_identifier
            fistcheck = False
        if not re.match(r'^\*{8,}$', user.plain_password) and fistcheck:
          user.password = hashSHA1(user.plain_password, salt)
      group_uuid = json.get('group_id', None)

      if group_uuid:
        group = self.group_broker.get_by_uuid(group_uuid)
        user.group_id = group.identifier
        user.group = group
      else:
        user.group_id = None
        user.group = None

      return user

  def assemble_server_mode(self, json, parent):
    server_mode = ServerMode('0', parent, 'mode_code')
    if json:
      server_mode.is_pull = json.get('is_pull', False)
      server_mode.is_push = json.get('is_push', False)
    return server_mode

  def assemble_sync_server(self, json, cache_object):

    if json:

      server = SyncServer()
      self.set_base(server, json, cache_object, None)

      server.name = json.get('name', None)
      server.description = json.get('description', None)
      server.type_id = json.get('type_id', None)
      server.baseurl = json.get('baseurl', None)
      server.baseurl = json.get('baseurl', None)
      server.api_key = json.get('api_key', None)
      server.certificate = json.get('certificate', None)
      server.ca_certificate = json.get('ca_certificate', None)
      server.verify_ssl = json.get('verify_ssl', False)
      # permissions setting
      self.mode = self.assemble_server_mode(json.get('mode', None), server)

      user_uuid = json.get('user_id', None)
      if not user_uuid:
        user = json.get('user', None)
        user_uuid = user.get('identifier', None)
      if user_uuid:
        user = self.user_broker.get_by_uuid(user_uuid)
        server.user = user
        server.user_id = user.identifier
      return server

  def assemble_condition(self, json, cache_object):
    if json:

      condition = Condition()
      self.set_base(condition, json, cache_object, None)
      condition.value = json.get('value', None)
      condition.description = json.get('description', None)
      return condition

  def assemble_mail_template(self, json, cache_object):
    if json:
      mail_template = MailTemplate()
      self.set_base(mail_template, json, cache_object, None)
      mail_template.name = json.get('name', None)
      mail_template.body = json.get('body', None)
      mail_template.subject = json.get('subject', None)
      return mail_template

  def assemble_attribute_type(self, json, cache_object):
    if json:
      attr_type = AttributeType()
      self.set_base(attr_type, json, cache_object, None)
      attr_type.name = json.get('name', None)
      attr_type.description = json.get('description', None)
      allowed_table = json.get('allowed_table', None)
      if allowed_table:
        attr_type.table_id = allowed_table.get('identifier')
      return attr_type

  def assemble_object_definition(self, json, cache_object):
    if json:
      obj_def = ObjectDefinition()
      self.set_base(obj_def, json, cache_object, None)

      obj_def.name = json.get('name', None)
      obj_def.description = json.get('description', None)
      obj_def.default_share = json.get('default_share', False)

      # The user cannot set this
      # obj_def.cybox_std = json.get('cybox_std', False)
      obj_def.cybox_std = False

      """
      chksum = json.get('chksum', None)
      if chksum:
        obj_def.chksum = chksum
      else:
        obj_def.chksum = gen_obj_chksum(obj_def)
      """
      # The chksum is always computed
      obj_def.chksum = gen_obj_chksum(obj_def)

      attrs = json.get('attributes', list())
      for attr in attrs:
        uuid = attr.get('identifier')
        try:
          attribute = self.attr_def_broker.get_by_uuid(uuid)
        except NothingFoundException:
          attribute = self.assemble_attribute_definition(attr, cache_object)
        except BrokerException as error:
          raise AssemblerException(error)
        obj_def.attributes.append(attribute)
      return obj_def
