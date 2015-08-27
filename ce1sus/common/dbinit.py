# -*- coding: utf-8 -*-

"""
(Description)

Created on Aug 10, 2015
"""


from __builtin__ import True
from ce1sus.helpers.common import strings
from datetime import datetime
import json

from ce1sus.common.classes.cacheobject import CacheObject
from ce1sus.common.system import DB_REL
from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.conditions import ConditionController
from ce1sus.controllers.admin.mails import MailController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.common.assembler.assembler import Assembler
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.classes.cstix.common.vocabstring import VocabString
from ce1sus.db.classes.cstix.extensions.test_mechanism.generic_test_mechanism import GenericTestMechanism
from ce1sus.db.classes.cstix.extensions.marking.simple_markings import SimpleMarkingStructure
from ce1sus.db.classes.internal.attributes.attribute import Condition
from ce1sus.db.classes.internal.backend.config import Ce1susConfig
from ce1sus.db.classes.internal.backend.mailtemplate import MailTemplate
from ce1sus.db.classes.internal.backend.types import AttributeType
from ce1sus.db.classes.internal.definitions import AttributeDefinition, ObjectDefinition
from ce1sus.db.classes.internal.report import ReferenceDefinition
from ce1sus.db.classes.internal.usrmgt.group import Group
from ce1sus.db.classes.internal.usrmgt.user import User
from ce1sus.db.common.session import SessionManager, Base
from ce1sus.helpers.common.hash import hashSHA1
from maintenance import Maintenance


__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


def get_users(config):
  salt = config.get('ce1sus', 'salt')

  result = list()
  # Add admin user
  user = User()
  user.identifier = 1
  user.uuid = 'f49eb0ed-438d-49ef-aa19-1d615a3ba01d'
  user.name = 'Root'
  user.sirname = 'Administrator'
  user.username = 'admin'
  user.password = hashSHA1('admin' + salt)
  user.last_login = None
  user.email = 'admin@example.com'
  user.api_key = None
  user.gpg_key = None
  user.activated = datetime.now()
  user.dbcode = 31
  user.activation_sent = None
  user.activation_str = 'e96e0b6cfdb77c4e957508315bf7b7124aea9fa0'
  user.api_key = '4a5e3a7e8aa200cbde64432df11c4b459b154499'
  user.created_at = strings.stringToDateTime("2015-08-14T07:56:34")
  user.modified_on = strings.stringToDateTime("2015-08-14T07:56:34")
  group = Group()
  group.uuid = 'fa2924e9-67c0-4f13-a7d2-d66cb499677e'
  group.name = 'Administrators'
  group.description = 'Administrators group'
  group.tlp_lvl = 0
  group.dbcode = 31
  group.default_dbcode = 31
  group.email = 'admin@example.com'
  group.created_at = strings.stringToDateTime("2015-08-14T07:56:34")
  group.modified_on = strings.stringToDateTime("2015-08-14T07:56:34")
  user.group = group
  result.append(user)
  return result


def get_mail_templates(user):
  result = list()
  mail = MailTemplate()
  mail.identifier = 1
  mail.uuid = 'fa6ac2c1-f504-4820-affe-d724f4817af9'
  mail.name = 'Publication'
  mail.body = '==============================================\nURL : ${event_url}\nEvent : ${event_uuid}\n==============================================\n'
  mail.body = mail.body + 'Title : ${event_title}\nDate : ${event_created}\nReported by : ${event_reporter}\nRisk : ${event_risk}\nAnalysis : ${event_analysis}\n'
  mail.body = mail.body + 'Description :\n${event_description}\n==============================================\nRelated to :\n${event_relations}\n'
  mail.body = mail.body + '==============================================\nEvent Objects :\n\n\n${event_objects}\n============================================== '
  mail.subject = 'Event[${event_id}] ${event_uuid} Published - ${event_tlp} - ${event_risk} - ${event_title}'
  mail.creator = user
  mail.modifier = user
  mail.created_at = strings.stringToDateTime("2015-08-14T07:56:34")
  mail.modified_on = strings.stringToDateTime("2015-08-14T07:56:34")
  result.append(mail)

  mail = MailTemplate()
  mail.identifier = 2
  mail.name = 'Update'
  mail.uuid = '36f5e3f9-7b54-4191-8f07-a20b8cf2fcb0'
  mail.body = '==============================================\nURL : ${event_url}\nEvent : ${event_uuid}\n==============================================\n'
  mail.body = mail.body + 'Title : ${event_title}\nDate : ${event_created}\nReported by : ${event_reporter}\nRisk : ${event_risk}\nAnalysis : ${event_analysis}\n'
  mail.body = mail.body + 'Description :\n${event_description}\n==============================================\nRelated to :\n${event_relations}\n'
  mail.body = mail.body + '==============================================\nEvent Objects :\n\n\n${event_objects}\n==============================================\n'
  mail.body = mail.body + '==============================================\nUpdated Relations :\n\${event_updated_relations}\n==============================================\n'
  mail.body = mail.body + 'Updated Objects :\n${event_updated_objects}\n==============================================\nUpdated Objects :\n${event_updated_objects}\n==============================================\n'
  mail.subject = 'Event[${event_id}] ${event_uuid} Updated - ${event_tlp} - ${event_risk} - ${event_title}'
  mail.creator = user
  mail.modifier = user
  mail.created_at = strings.stringToDateTime("2015-08-14T07:56:34")
  mail.modified_on = strings.stringToDateTime("2015-08-14T07:56:34")
  result.append(mail)

  mail = MailTemplate()
  mail.identifier = 3
  mail.name = 'Activation'
  mail.uuid = '5c0cf7a9-7337-47f9-bb48-ff291a1ee1c6'
  mail.body = 'Welcome to the Ce1sus community. Your user account has been created and has to be activated over the following link:\n\n'
  mail.body = mail.body + '${activation_link}\n\nNote: The activation is valid for 24 hours.\n\nThe normal page of the system you can by accessed at the following URL:\n\n'
  mail.body = mail.body + '${ce1sus_url}\n\nYour login credentials are as follow:\n\nUsername: ${username}\n\nPassword: ${password}\n\nTo activate your account please visit the following link\n\n'
  mail.body = mail.body + 'We hope that you find the information contained in our database useful and we\'re looking forward to all the valuable information that you\'ll be able to share with us.\n\n'
  mail.body = mail.body + 'Please keep in mind that all users and organisations have to conform to the Terms of Use, they are there to make sure that this community works based on trust and that there is fair contribution of validated and valuable data into Ce1sus.\n\n'
  mail.body = mail.body + 'If you run into any issues or have any feedback regarding Ce1sus, don\'t hesitate to contact us at ce1sus@ce1sus.lan\n\n'
  mail.body = mail.body + 'Looking forward to fostering the collaboration between our organisations through your active participation in this information sharing program.\n\n'
  mail.body = mail.body + 'Best Regards,\n\n'
  mail.subject = 'User Registration'
  mail.creator = user
  mail.modifier = user
  mail.created_at = strings.stringToDateTime("2015-08-14T07:56:34")
  mail.modified_on = strings.stringToDateTime("2015-08-14T07:56:34")
  result.append(mail)

  return result


def get_attribute_type_definitions():
  attribute_type = AttributeType()
  attribute_type.identifier = 1
  attribute_type.name = 'None'
  attribute_type.uuid = 'a47fef10-298c-4731-8480-320cb34989c1'
  attribute_type.description = 'This type is used when no type has been specified'
  attribute_type.table_id = None
  attribute_type.created_at = strings.stringToDateTime("2015-08-14T07:56:34")
  attribute_type.modified_on = strings.stringToDateTime("2015-08-14T07:56:34")
  return {attribute_type.uuid: attribute_type}


def dbinit(config, json_location=''):
  print "Getting config"
  config.get_section('Logger')['log'] = False
  print "Creating DB"
  session = SessionManager(config)
  engine = session.connector.get_engine()
  getattr(Base, 'metadata').create_all(engine, checkfirst=True)
  print "Populating DB and checking/creating gpg db"
  mysql_session = session.connector.get_direct_session()
  session = mysql_session
  user_ctrl = UserController(config, session)
  assembler = Assembler(config, session)
  handler_broker = AttributeHandlerBroker(session)
  print "Populate users"
  all_users = get_users(config)
  users = list()
  for user in all_users:
    user_ctrl.insert_user(user, False, False, False)
    users.append(user)
  user_ctrl.user_broker.do_commit(True)

  # Add handlers
  maintenance = Maintenance(config)

  # Register handlers
  print "Registering handlers"

  maintenance.register_handler('generichandler', 'attributes', 'GenericHandler', True)
  maintenance.register_handler('texthandler', 'attributes', 'TextHandler')
  maintenance.register_handler('multiplegenerichandler', 'attributes', 'MultipleGenericHandler', True)
  maintenance.register_handler('filehandler', 'attributes', 'FileHandler', True)
  maintenance.register_handler('datehandler', 'attributes', 'DateHandler', True)
  maintenance.register_handler('cbvaluehandler', 'attributes', 'CBValueHandler', True)
  maintenance.register_handler('emailhandler', 'attributes', 'EmailHandler', True)
  maintenance.register_handler('filehandler', 'attributes', 'FileWithHashesHandler', True)

  maintenance.register_handler('filehandler', 'references', 'FileReferenceHandler', True)
  maintenance.register_handler('generichandler', 'references', 'GenericHandler', True)
  maintenance.register_handler('linkhandler', 'references', 'LinkHandler', True)
  maintenance.register_handler('rthandler', 'references', 'RTHandler', True)
  maintenance.register_handler('texthandler', 'references', 'TextHandler', True)


  mail_templates = get_mail_templates(users[0])
  print "Populating Mail templates"
  mail_ctrl = MailController(config, session)

  for mail_template in mail_templates:
    mail_ctrl.insert_mail(mail_template, False)
  mail_ctrl.mail_broker.do_commit(False)

  all_attr_types = get_attribute_type_definitions()
  attr_types = dict()
  print "Populating attribute types"
  attr_ctrl = AttributeDefinitionController(config, session)

  for key, value in all_attr_types.iteritems():

    attr_ctrl.insert_attribute_type(value, False)
    attr_types[key] = value

  attr_ctrl.type_broker.do_commit(False)

  cond_ctrl = ConditionController(config, session)

  cache_object = CacheObject()
  cache_object.user = users[0]
  cache_object.insert = True
  cache_object.rest_insert = False
  cache_object.owner = True

  with open(json_location + 'conditions.json') as data_file:
    all_conditions = json.load(data_file)
  print "Populating conditions"
  for condition_json in all_conditions:
    condition = assembler.assemble(condition_json, Condition, None, cache_object)
    cond_ctrl.insert_condition(condition, False)
  cond_ctrl.condition_broker.do_commit(True)


  # add attributes definitions

  with open(json_location + 'attributes.json') as data_file:
    attrs = json.load(data_file)
  print "Populating attribute definitions"
  attr_dict = dict()
  for attr_json in attrs:
    attr_def = assembler.assemble(attr_json, AttributeDefinition, None, cache_object)
    attr_def.cybox_std = attr_json.get('cybox_std', False)
    attr_ctrl.insert_attribute_definition(attr_def, False)

    attr_dict[attr_def.uuid] = attr_def

  attr_ctrl.attr_def_broker.do_commit(False)

  # add object definitions and make relations
  with open(json_location + 'objects.json') as data_file:
    objs = json.load(data_file)

  obj_ctrl = ObjectDefinitionController(config, session)
  print "Populating object definitions"
  for obj_json in objs:
    obj_def = assembler.assemble(obj_json, ObjectDefinition, None, cache_object)
    obj_def.cybox_std = obj_json.get('cybox_std', False)
    obj_ctrl.insert_object_definition(obj_def, False)

  obj_ctrl.obj_def_broker.do_commit(False)

  ref_ctrl = ReferencesController(config, session)

  with open(json_location + 'references.json') as data_file:
    references = json.load(data_file)
  print "Populating references definitions"
  for ref_json in references:
    ref_def = assembler.assemble(ref_json, ReferenceDefinition, None, cache_object)
    ref_ctrl.insert_reference_definition(ref_def, False)

  ref_ctrl.reference_definition_broker.do_commit(True)

  # Add config elements
  conf = Ce1susConfig()
  conf.key = 'db_shema'
  conf.value = DB_REL
  ref_ctrl.reference_definition_broker.session.add(conf)
  ref_ctrl.reference_definition_broker.do_commit(True)
