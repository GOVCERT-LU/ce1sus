# -*- coding: utf-8 -*-

"""
(Description)

Created on Oct 16, 2014
"""


import json
import os
import sys

basePath = os.path.dirname(os.path.abspath(__file__)) + '/../../'
sys.path.insert(0, '../../')

from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.conditions import ConditionController
from ce1sus.controllers.admin.mails import MailController
from ce1sus.controllers.admin.user import UserController
from ce1sus.db.brokers.definitions.handlerdefinitionbroker import AttributeHandlerBroker
from ce1sus.db.classes.attribute import Condition
import ce1sus.db.classes.attribute
from ce1sus.db.classes.definitions import AttributeDefinition, ObjectDefinition
import ce1sus.db.classes.definitions
import ce1sus.db.classes.event
import ce1sus.db.classes.indicator
import ce1sus.db.classes.log
import ce1sus.db.classes.mailtemplate
import ce1sus.db.classes.object
import ce1sus.db.classes.observables
import ce1sus.db.classes.relation
import ce1sus.db.classes.report
import ce1sus.db.classes.servers
import ce1sus.db.classes.processitem
from ce1sus.db.classes.types import AttributeType
import ce1sus.db.classes.types
import ce1sus.db.classes.ttp
from ce1sus.db.classes.user import User
import ce1sus.db.classes.user
import ce1sus.db.classes.values
from ce1sus.db.common.session import SessionManager, Base
from ce1sus.helpers.common.config import Configuration
from maintenance import Maintenance
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.db.classes.report import ReferenceDefinition

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'


if __name__ == '__main__':

  # want parent of parent directory aka ../../
  # setup cherrypy
  #
  ce1susConfigFile = basePath + 'config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  print "Getting config"
  config.get_section('Logger')['log'] = False
  print "Creating DB"
  session = SessionManager(config)
  mysql_session = session.connector.get_direct_session()
  session = mysql_session

  # add attributes definitions

  obj_ctrl = ObjectDefinitionController(config, session)
  ref_ctrl = ReferencesController(config, session)
  attr_ctrl = AttributeDefinitionController(config, session)
  handler_broker = AttributeHandlerBroker(session)
  cond_ctrl = ConditionController(config, session)

  # user
  user_controller = UserController(config, session)
  user_uuid = config.get('ce1sus', 'maintenaceuseruuid', None)
  user = user_controller.get_user_by_uuid(user_uuid)

  all_bd_defs = attr_ctrl.get_all_attribute_definitions()
  attr_defs = dict()
  for attr_def in all_bd_defs:
    attr_defs[attr_def.uuid] = attr_def

  all_bd_defs = obj_ctrl.get_all_object_definitions()
  obj_defs = dict()
  for obj_def in all_bd_defs:
    obj_defs[obj_def.uuid] = obj_def

  all_bd_defs = ref_ctrl.get_reference_definitions_all()
  ref_defs = dict()
  for ref_def in all_bd_defs:
    ref_defs[ref_def.uuid] = ref_def

  with open('../install/database/attributes.json') as data_file:
    attrs = json.load(data_file)

  print "Updating attribute definitions"

  for attr_json in attrs:
    # check if exists
    uuid = attr_json.get('identifier')
    attr_def = attr_defs.get(uuid, None)

    if attr_def is None:
      attr_def = AttributeDefinition()
      attr_def.uuid = uuid
      new_one = True
    else:
      new_one = False
    attr_def.populate(attr_json)
    attr_def.uuid = attr_json.get('identifier')
    attributehandler_uuid = attr_json.get('attributehandler_id', None)
    attribute_handler = handler_broker.get_by_uuid(attributehandler_uuid)
    attr_def.attributehandler_id = attribute_handler.identifier
    attr_def.attribute_handler = attribute_handler

    value_type_uuid = attr_json.get('type_id', None)
    value_type = attr_ctrl.type_broker.get_by_uuid(value_type_uuid)

    attr_def.value_type_id = value_type.identifier

    default_condition_uuid = attr_json.get('default_condition_id', None)

    default_condition = cond_ctrl.get_condition_by_uuid(default_condition_uuid)
    attr_def.default_condition_id = default_condition.identifier

    if new_one:
      attr_ctrl.insert_attribute_definition(attr_def, user, False)
    else:
      attr_ctrl.attr_def_broker.update(attr_def, False)

    attr_defs[attr_def.uuid] = attr_def

  attr_ctrl.attr_def_broker.do_commit(False)

  # add object definitions and make relations
  with open('../install/database/objects.json') as data_file:
    objs = json.load(data_file)

  obj_ctrl = ObjectDefinitionController(config, session)
  print "Updating object definitions"
  for obj_json in objs:

    uuid = obj_json.get('identifier')
    obj_def = obj_defs.get(uuid, None)
    if obj_def is None:
      obj_def = ObjectDefinition()
      obj_def.uuid = uuid
      new = True
    else:
      new = False

    obj_def.populate(obj_json)
    attrs = obj_json.get('attributes')
    # clear all relations in case
    obj_def.attributes = list()
    for attr in attrs:
      attr_uuid = attr.get('identifier')
      obj_def.attributes.append(attr_defs[attr_uuid])

    if new:
      obj_ctrl.insert_object_definition(obj_def, user, False)
    else:
      obj_ctrl.obj_def_broker.update(obj_def, False)

  obj_ctrl.obj_def_broker.do_commit(False)

  ref_ctrl = ReferencesController(config, session)

  with open('../install/database/references.json') as data_file:
    references = json.load(data_file)
  print "Updating references definitions"
  for ref_json in references:
    uuid = ref_json.get('identifier')
    ref_def = ref_defs.get(uuid, None)
    if ref_def is None:
      ref_def = ReferenceDefinition()
      ref_def.uuid = uuid
      new = True
    else:
      new = False

    ref_def.populate(ref_json)

    referencehandler_uuid = ref_json.get('referencehandler_id', None)
    reference_handler = ref_ctrl.reference_broker.get_handler_by_uuid(referencehandler_uuid)
    ref_def.referencehandler_id = reference_handler.identifier
    ref_def.reference_handler = reference_handler

    if new:
      ref_ctrl.insert_reference_definition(ref_def, user, False)
    else:
      ref_ctrl.update_reference(ref_def, user, False)

  ref_ctrl.reference_definition_broker.do_commit(False)
