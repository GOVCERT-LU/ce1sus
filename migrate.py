# -*- coding: utf-8 -*-

"""
(Description)

Created on Jan 8, 2015
"""


import copy
import dateutil
import json
from os.path import dirname, abspath
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.dynamic import AppenderQuery
from sqlalchemy.orm.session import make_transient
from types import ListType
from uuid import uuid4

from ce1sus.controllers.admin.attributedefinitions import AttributeDefinitionController
from ce1sus.controllers.admin.conditions import ConditionController
from ce1sus.controllers.admin.group import GroupController
from ce1sus.controllers.admin.objectdefinitions import ObjectDefinitionController
from ce1sus.controllers.admin.references import ReferencesController
from ce1sus.controllers.admin.user import UserController
from ce1sus.controllers.base import ControllerException, ControllerIntegrityException
from ce1sus.controllers.events.event import EventController
from ce1sus.controllers.events.indicatorcontroller import IndicatorController
from ce1sus.db.classes.attribute import Attribute
import ce1sus.db.classes.attribute
import ce1sus.db.classes.definitions
from ce1sus.db.classes.event import Event, EventGroupPermission
import ce1sus.db.classes.event
from ce1sus.db.classes.group import Group
from ce1sus.db.classes.indicator import Indicator
import ce1sus.db.classes.indicator
import ce1sus.db.classes.mailtemplate
from ce1sus.db.classes.object import Object, RelatedObject
import ce1sus.db.classes.object
from ce1sus.db.classes.observables import Observable, ObservableComposition, \
  RelatedObservable
import ce1sus.db.classes.observables
import ce1sus.db.classes.relation
from ce1sus.db.classes.report import Report, Reference
from ce1sus.db.classes.types import AttributeType
import ce1sus.db.classes.types
from ce1sus.db.classes.user import User
import ce1sus.db.classes.user
import ce1sus.db.classes.values
from ce1sus.db.common.session import SessionManager, Base
from ce1sus.depricated.helpers.bitdecoder import BitRight
from ce1sus.handlers.attributes.generichandler import GenericHandler
from ce1sus.helpers.common import strings
from ce1sus.helpers.common.config import Configuration
from ce1sus.helpers.common.debug import Log
from ce1sus.helpers.common.objects import get_fields, get_class


attribute_id_uuid = dict()
resource_id_uuid = dict()
logger = None
types = None

__author__ = 'Weber Jean-Paul'
__email__ = 'jean-paul.weber@govcert.etat.lu'
__copyright__ = 'Copyright 2013-2014, GOVCERT Luxembourg'
__license__ = 'GPL v3+'
notmapped = None


def map_group(line, groups, owner):
  group = groups[line['identifier']]
  grouppermission = EventGroupPermission()
  grouppermission.group = group
  grouppermission.group_id = group.identifier
  grouppermission.dbcode = group.default_dbcode
  # Set the informations to the owner of the event
  grouppermission.creator_group = owner.group
  grouppermission.creator_group_id = grouppermission.creator_group.identifier
  grouppermission.creator = owner
  grouppermission.creator_id = grouppermission.creator.identifier
  grouppermission.modifier = owner
  grouppermission.modifier_id = grouppermission.modifier.identifier
  grouppermission.originating_group = grouppermission.creator_group
  grouppermission.originating_group_id = grouppermission.creator_group.identifier
  return grouppermission


def map_condition(name, conditions):
  for condition in conditions:
    if condition.value == name:
      return condition


def map_obj_def(line, definitions):
  name = line['name']
  if 'file' in name:
    name = 'file'
  elif name == 'victim_targeting':
    return None
  chksum = line['chksum']
  found_def = None
  for definition in definitions:
    if name == definition.name or chksum == definition.chksum:
      found_def = definition
      break
  if found_def:
    return found_def
  else:
    raise Exception(u'Object Definition {0} with chksum {1} not found in new setup'.format(name, chksum))


def map_reference_definition(line, definitions):
  name = line['name']
  if name == 'raw_document_file':
    name = 'raw_file'
  if name == 'reference_url':
    name = 'link'
  if name == 'url':
    name = 'link'
  if name == 'mutex':
    return None
  chksum = line['chksum']
  found_def = None
  for definition in definitions:
    if name == definition.name or chksum == definition.chksum:
      found_def = definition
      break
  if found_def:
    return found_def
  else:
    raise Exception(u'Reference Definition {0} with chksum {1} not found in new setup'.format(name, chksum))


def map_attr_def(line, definitions):
  name = line['name']
  if name == 'email_receive_datetime':
    return None
  elif name == 'email_send_datetime':
    return None
  elif name == 'reference_url':
    return None
  elif name == 'ipv4_addr_c&c':
    name = 'ipv4_addr'
  elif name == 'ip_protocol':
    name = 'Protocol'
  elif name == 'ip_port':
    name = 'Port'
  elif name == 'description':
    name = 'comment'
  elif name == 'analysis_free_text':
    name = 'comment'
  elif 'named_pipe' in name:
    name = 'Pipe_Name'
  elif name == 'domain':
    name = 'DomainName_Value'
  elif name == 'http_method':
    name = 'HTTP_Method'
  chksum = line['chksum']
  for definition in definitions:
    if name == definition.name or chksum == definition.chksum:
      return definition
  raise Exception(u'Attribtue Definition {0} with chksum {1} not found in new setup'.format(name, chksum))


def map_attribute(line, attr_defs, users, obj, owner, conditions):
  if obj.definition.name == 'email':
    if line['definition']['name'] == 'raw_file' or line['definition']['name'] == 'file_name' or line['definition']['name'] == 'email_server':
      return None
  if obj.definition.name == 'Code':
    if line['definition']['name'] == 'hash_sha1':
      return None

  attribute = Attribute()
  attribute.identifier = line['uuid']
  attribute.dbcode = line['dbcode']
  attribute_id_uuid[line['identifier']] = attribute
  attribute.creator_group = groups[line['creator_group_id']]
  attribute.creator_group_id = attribute.creator_group.identifier
  attribute.creator = users[line['creator_id']]
  attribute.creator_id = attribute.creator.identifier
  modifier_id = line.get('modifier_id')
  if modifier_id:
    modifier = users[modifier_id]
  else:
    modifier = obj.creator
  attribute.is_ioc = line['ioc'] == 1 or line['ioc'] == '1'
  attribute.modifier = modifier
  attribute.modifier_id = obj.modifier.identifier
  attribute.originating_group = attribute.creator_group
  attribute.originating_group_id = attribute.creator_group.identifier
  parent_id = line['attr_parent_id']
  if parent_id:
    parent = attribute_id_uuid.get(parent_id, None)
    # TODO: To check this again!
    if parent:
      parent.children.append(attribute)

  try:
    if 'pattern' in line['definition']['name']:
      line['definition']['name'] = line['definition']['name'].replace('_pattern', '')
      attribute.condition = map_condition('FitsPattern', conditions)
    else:
      attribute.condition = map_condition('Equals', conditions)
    definition = map_attr_def(line['definition'], attr_defs)
  except Exception as error:
    raise error
  if definition:
    attribute.definition = definition
  else:
    notmapped.write('Attribute Could not be mapped as definition is missing for the new object {0}\n'.format(obj.identifier))
    notmapped.write('{0}\n'.format(json.dumps(line)))
    return None

  attribute.object = obj
  attribute.object_id = attribute.object.identifier

  attribute.value = line['value']

  if 'c&c' in line['definition']:
    # attach a depricated c&c attribute
    line['uuid'] = '{0}'.format(uuid4())
    line['definition']['name'] = 'is_c&c'
    line['definition']['chksum'] = 0
    line['value'] = 1
    atribute = map_attribute(line, attr_defs, users, obj, owner, conditions)
    obj.attributes.append(atribute)

  logger.info('Created attribute {0}'.format(attribute))
  return attribute


def create_related_obj(parent, child):
  related_obj = RelatedObject()
  related_obj.parent = parent
  related_obj.parent_id = related_obj.parent.identifier
  related_obj.object = child
  related_obj.child_id = related_obj.object.identifier
  logger.info('Created related object {0}'.format(related_obj))
  return related_obj


def create_related_observable(parent, child):
  related_observable = RelatedObservable()
  related_observable.parent = parent
  related_observable.parent_id = related_observable.parent.identifier
  related_observable.observable = child
  related_observable.child_id = related_observable.observable.identifier
  related_observable.creator_group = child.creator_group
  related_observable.creator_group_id = related_observable.creator_group.identifier
  related_observable.creator = child.creator
  related_observable.creator_id = related_observable.creator.identifier
  related_observable.modifier = child.modifier
  related_observable.modifier_id = related_observable.modifier.identifier
  related_observable.originating_group = related_observable.creator_group
  related_observable.originating_group_id = related_observable.creator_group.identifier

  logger.info('Created related observable {0}'.format(related_observable))
  return related_observable

seen_objects = list()


def make_object(line, observable, groups, users):
  obj = Object()
  obj.observable_id = observable.identifier
  obj.observable = observable
  obj.identifier = line['uuid']
  obj.creator_group = groups[line['creator_group_id']]
  obj.creator_group_id = obj.creator_group.identifier
  obj.creator = users[line['creator_id']]
  obj.creator_id = obj.creator.identifier
  modifier_id = line['modifier_id']
  obj.dbcode = line['dbcode']
  if modifier_id:
    modifier = users[modifier_id]
  else:
    modifier = obj.creator
  obj.modifier = modifier
  obj.modifier_id = obj.modifier.identifier
  obj.originating_group = obj.creator_group
  obj.originating_group_id = obj.creator_group.identifier
  return obj


def map_cybox(line, users, groups, owner, attr_defs, obj_defs, observable, event, conditions):
  seen_objects.append(line['identifier'])
  obj = make_object(line, observable, groups, users)
  if line['definition']['name'] == 'network_traffic':
    # Most these are pcaps hence building a file with a raw atrifact.
    # the definition of this object is file
    definition = map_obj_def({'name': 'file', 'chksum': None}, obj_defs)
    obj.definition = definition
    # set attributes for filename etc
    attribute_line = None
    for element in line['attributes']:
      if element['definition']['name'] == 'file_name':
        attribute_line = element
        break

    # remove the assigned attributes from the object
    line['attributes'].remove(attribute_line)

    attribtue = map_attribute(attribute_line, attr_defs, users, obj, owner, conditions)
    obj.attributes.append(attribtue)

    # then attach the raw artifact
    raw_artifact = make_object(line, observable, groups, users)
    raw_artifact.identifier = uuid4()
    raw_artifact.definition = map_obj_def({'name': 'Artifact', 'chksum': None}, obj_defs)
    # set attributes for type and data
    attribute_line = None
    for element in line['attributes']:
      if element['definition']['name'] == 'raw_pcap_file':
        attribute_line = element
        break
    line['attributes'].remove(attribute_line)
    attribute_line['definition']['name'] = 'raw_artifact'
    attribtue = map_attribute(attribute_line, attr_defs, users, raw_artifact, owner, conditions)
    raw_artifact.attributes.append(attribtue)
    # set the type
    attribute_line['uuid'] = uuid4()
    attribute_line['definition']['name'] = 'artifact_type'
    attribute_line['value'] = 'Network Traffic'
    attribtue = map_attribute(attribute_line, attr_defs, users, raw_artifact, owner, conditions)
    raw_artifact.attributes.append(attribtue)

    # attach the object
    obj.related_objects.append(create_related_obj(obj, raw_artifact))

    pass
  elif 'file' in line['definition']['name']:

    definition = map_obj_def({'name': 'file', 'chksum': None}, obj_defs)
    obj.definition = definition

    attribute_line = None
    for element in line['attributes']:
      if element['definition']['name'] == 'raw_file' or element['definition']['name'] == 'raw_document_file':
        if attribute_line:
          # there are 2 attributes with raw file -> impossible to determine hat is what
          notmapped.write('{0} could not be mapped for file on new object {1} as it contains 2 files\n'.format(line['definition']['name'], obj.identifier))
          notmapped.write('{0}\n'.format(json.dumps(line)))
          return None
        else:
          attribute_line = element

    if attribute_line:
      line['attributes'].remove(attribute_line)
      # do the artifact
      # then attach the raw artifact
      raw_artifact = make_object(line, observable, groups, users)
      raw_artifact.identifier = uuid4()
      raw_artifact.definition = map_obj_def({'name': 'Artifact', 'chksum': None}, obj_defs)

      attribute_line['definition']['name'] = 'raw_artifact'
      attribtue = map_attribute(attribute_line, attr_defs, users, raw_artifact, owner, conditions)
      raw_artifact.attributes.append(attribtue)
      # set the type
      attribute_line['definition']['name'] = 'artifact_type'
      attribute_line['value'] = 'File'
      attribute_line['uuid'] = uuid4()
      attribtue = map_attribute(attribute_line, attr_defs, users, raw_artifact, owner, conditions)
      raw_artifact.attributes.append(attribtue)

      # append to the object
      obj.related_objects.append(create_related_obj(obj, raw_artifact))
  elif line['definition']['name'] == 'source_code':

    definition = map_obj_def({'name': 'Code', 'chksum': None}, obj_defs)
    obj.definition = definition

    attribute_hash = None
    attribute_file = None
    attribute_file_name = None
    for element in line['attributes']:
      if element['definition']['name'] == 'raw_file' or element['definition']['name'] == 'raw_document_file':
        attribute_file = element
      elif element['definition']['name'] == 'file_name':
        attribute_file_name = element
      elif element['definition']['name'] == 'hash_sha1':
        attribute_hash = element

    file_obj = make_object(line, observable, groups, users)
    file_obj.identifier = uuid4()
    file_obj.definition = map_obj_def({'name': 'file', 'chksum': None}, obj_defs)
    if attribute_hash:
      line['attributes'].remove(attribute_hash)
      attribtue = map_attribute(attribute_hash, attr_defs, users, file_obj, owner, conditions)
      file_obj.attributes.append(attribtue)
    if attribute_file_name:
      line['attributes'].remove(attribute_file_name)
      attribtue = map_attribute(attribute_file_name, attr_defs, users, file_obj, owner, conditions)
      file_obj.attributes.append(attribtue)
    # append to the object
    obj.related_objects.append(create_related_obj(obj, file_obj))

    if attribute_file:
      line['attributes'].remove(attribute_file)
      # do the artifact
      # then attach the raw artifact
      raw_artifact = make_object(line, observable, groups, users)
      raw_artifact.identifier = uuid4()
      raw_artifact.definition = map_obj_def({'name': 'Artifact', 'chksum': None}, obj_defs)

      attribute_file['definition']['name'] = 'raw_artifact'
      attribtue = map_attribute(attribute_file, attr_defs, users, raw_artifact, owner, conditions)
      raw_artifact.attributes.append(attribtue)
      # set the type
      attribute_file['definition']['name'] = 'artifact_type'
      attribute_file['value'] = 'File'
      attribute_file['uuid'] = uuid4()
      attribtue = map_attribute(attribute_file, attr_defs, users, raw_artifact, owner, conditions)
      raw_artifact.attributes.append(attribtue)

      # append to the object
      file_obj.related_objects.append(create_related_obj(file_obj, raw_artifact))
  else:
    definition = map_obj_def(line['definition'], obj_defs)
    if definition:
      obj.definition = definition
    else:
      notmapped.write('Object Could not be mapped as definition is missing for the new observable {0}\n'.format(observable.identifier))
      notmapped.write('{0}\n'.format(json.dumps(line)))
      return None
      # set attributes
  for attribute in line['attributes']:
    attribute = map_attribute(attribute, attr_defs, users, obj, owner, conditions)
    if attribute:
      obj.attributes.append(attribute)

  if line.get('children'):
    for child in line['children']:
      mapped = None
      if child['definition']['name'] == 'ioc_records':
          # TODO map ioc records
          mapped = map_ioc_records(child, users, groups, owner, attr_defs, obj_defs, observable, event, conditions)
          for obs in mapped:
            # attach this one as related observable to the parent observable
            observable.related_observables.append(create_related_observable(observable, obs))

          # -> composed observable
      elif 'reference' in child['definition']['name']:
        report = map_report(child, users, groups, event.creator, event, ressources)
        if report:
          event.reports.append(report)
      else:
        mapped = map_cybox(child, users, groups, owner, attr_defs, obj_defs, observable, event, conditions)
        if mapped:
          if mapped.identifier == obj.identifier:
            mapped.identifier = uuid4()
          related_object = create_related_obj(obj, mapped)
          obj.related_objects.append(related_object)
        pass
  logger.info('Created object {0}'.format(obj))
  return obj


def map_malicious_website(line, users, groups, owner, attr_defs, obj_defs, event, conditions):
  observable = make_observable(line, groups, users, event)
  observable.title = 'Malicious website'

  composed_attribute = ObservableComposition()
  composed_attribute.identifier = uuid4()
  composed_attribute.dbcode = line['dbcode']

  attributes = line['attributes']
  for attribtue in attributes:
    name = attribtue['definition']['name']
    if name == 'description':
      if not observable.description:
        observable.description = ''
      observable.description = observable.description + ' ' + attribtue['value']
    elif name == 'url':
      attribute = make_attr_obs(attribtue, users, groups, 'URI', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(attribute)
    elif name == 'url_path':
      # make pattern out of it
      attribute['value'] = u'*{0}'.format(attribute['value'])
      attribute['uuid'] = u'{0}'.format(uuid4())
      attribute['definition']['name'] = 'url_pattern'
      attribute['definition']['chksum'] = None
      attribute = make_attr_obs(attribtue, users, groups, 'URI', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(attribute)
    elif name == 'hostname':
      attribute = make_attr_obs(attribtue, users, groups, 'Hostname', 'Hostname_Value', owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(attribute)
    else:
      raise Exception(name)

  observable.observable_composition = composed_attribute

  # also create the indicators
  indicator = map_indicator(observable, line, users, groups, 'URL Watchlist')
  if indicator:
    event.indicators.append(indicator)
  return observable


def get_indicator_type(indicator_type):
  for type_ in types:
    if type_.name == indicator_type:
      return type_
  raise Exception('Type "{0}" is not defined'.format(indicator_type))


def clone_object(obj):
  new_obj = Object()
  # typical foo
  new_obj.modified_on = obj.modified_on
  new_obj.created_at = obj.created_at
  new_obj.creator = obj.creator
  new_obj.creator_id = new_obj.creator.identifier
  new_obj.modifier = obj.modifier
  new_obj.modifier_id = new_obj.modifier.identifier
  new_obj.originating_group = obj.originating_group
  new_obj.originating_group_id = new_obj.originating_group.identifier

  new_obj.definition = obj.definition
  new_obj.definition_id = new_obj.definition.identifier
  new_obj.dbcode = obj.dbcode

  new_obj.observable = obj.observable
  new_obj.observable_id = new_obj.observable.identifier
  new_obj.parent = new_obj.parent
  if new_obj.parent:
    new_obj.parent_id = new_obj.parent.identifer

  for attribute in obj.attributes:
    if attribute.is_ioc:
      new_obj.attributes.append(attribute)
  return new_obj


def clone_composed_observable(composed_observable):
  new_composed_observable = ObservableComposition()
  new_composed_observable.dbcode = composed_observable.dbcode
  new_composed_observable.operator = composed_observable.operator
  new_composed_observable.parent = composed_observable.parent
  new_composed_observable.parent_id = composed_observable.parent_id

  for obs in composed_observable.observables:
    new_composed_observable.observables.append(clone_observable(obs))
  return new_composed_observable


def clone_rel_observable(rel_observable, parent_obs):
  new_rel_observable = RelatedObservable()
  new_rel_observable.observable = clone_observable(rel_observable.observable)
  new_rel_observable.child_id = new_rel_observable.observable.identifier
  new_rel_observable.confidence = rel_observable.confidence

  new_rel_observable.parent = parent_obs
  new_rel_observable.parent_id = parent_obs.identifier
  new_rel_observable.relation = rel_observable.relation
  return new_rel_observable


def clone_observable(observable):
  new_observable = Observable()
  new_observable.title = observable.title
  new_observable.dbcode = observable.dbcode
  # do not set event as this will then be directly liked to the event!
  new_observable.parent = observable.parent
  new_observable.parent_id = observable.parent_id

  new_observable.description = observable.description

  # typical foo
  new_observable.modified_on = observable.modified_on
  new_observable.created_at = observable.created_at
  new_observable.creator = observable.creator
  new_observable.creator_id = new_observable.creator.identifier
  new_observable.modifier = observable.modifier
  new_observable.modifier_id = new_observable.modifier.identifier
  new_observable.originating_group = observable.originating_group
  new_observable.originating_group_id = new_observable.originating_group.identifier
  new_observable.creator_group = observable.creator_group
  new_observable.creator_group_id = new_observable.creator_group.identifier

  if observable.object:
    obj = clone_object(observable.object)
    new_observable.object = obj
  if observable.observable_composition:
    composed = clone_composed_observable(observable.observable_composition)
    new_observable.observable_composition = composed

  if observable.related_observables:
    for rel_obj in observable.related_observables:
      new_observable.related_observables.append(clone_rel_observable(rel_obj, new_observable))

  return new_observable


def map_indicator(observable, line, users, groups, indicator_type):
  indicator = Indicator()
  indicator.identifier = uuid4()
  indicator.creator_group = observable.creator_group
  indicator.creator_group_id = indicator.creator_group.identifier
  indicator.creator = observable.creator
  indicator.creator_id = indicator.creator.identifier
  indicator.modifier = observable.creator
  indicator.modifier_id = indicator.modifier.identifier
  indicator.originating_group = indicator.creator_group
  indicator.originating_group_id = indicator.creator_group.identifier

  if indicator_type:
    indicator.type_ .append(get_indicator_type(indicator_type))

  new_observable = clone_observable(observable)
  indicator.observables.append(new_observable)
  indicator.created_at = observable.created_at
  indicator.modified_on = observable.modified_on
  return indicator


def make_attr_obs(line, users, groups, obj_def, attr_def, owner, obj_defs, attr_defs, conditions):
  observable = make_observable(line, groups, users, event)
  observable.identifier = uuid4()

  obj = make_object(line, observable, groups, users)
  obj.identifier = uuid4()
  changed = False
  if attr_def == 'ip_port':
    obj.definition = map_obj_def({'name': 'SocketAddress', 'chksum': None}, obj_defs)
  elif attr_def == 'ip_protocol':
    obj.definition = map_obj_def({'name': 'NetworkSocket', 'chksum': None}, obj_defs)
  elif attr_def == 'ids_rules':
    value = line['value']
    if 'snort:' in value:
      line['value'] = value.replace('snort:', '')
      obj.definition = map_obj_def({'name': 'IDSRule', 'chksum': None}, obj_defs)
      line['definition']['name'] = 'snort_rule'
      line['definition']['chksum'] = None
      changed = True
    else:
      raise Exception('Uknown ids system {0}'.format(value))

  elif attr_def == 'yara_rule':
    obj.definition = map_obj_def({'name': 'IDSRule', 'chksum': None}, obj_defs)

  else:
    obj.definition = map_obj_def({'name': obj_def, 'chksum': None}, obj_defs)
  if not obj.definition:
    notmapped.write('{0} could not be mapped\n'.format(obj_def))
    notmapped.write('{0}\n'.format(json.dumps(line)))
    return None

  if not changed:
    line['definition']['name'] = attr_def
  attribute = map_attribute(line, attr_defs, users, obj, owner, conditions)
  obj.attributes.append(attribute)
  # make additional attribtues
  if attr_def == 'hostname':
    line['definition']['name'] = 'Naming_System'
    line['definition']['chksum'] = None
    line['uuid'] = u'{0}'.format(uuid4())
    line['value'] = 'DNS'
    attribute = map_attribute(line, attr_defs, users, obj, owner, conditions)
    obj.attributes.append(attribute)
  elif attr_def == 'url':
    line['definition']['name'] = 'URIType'
    line['definition']['chksum'] = None
    line['uuid'] = u'{0}'.format(uuid4())
    line['value'] = 'URL'
    attribute = map_attribute(line, attr_defs, users, obj, owner, conditions)
    obj.attributes.append(attribute)

  observable.object = obj

  return observable


def map_observable_composition(mal_email, line, users, groups, owner, event):
  result_observable = make_observable(line, groups, users, event)
  result_observable.identifier = uuid4()

  composed_attribute = ObservableComposition()
  composed_attribute.identifier = line['uuid']
  composed_attribute.dbcode = line['dbcode']
  report = None
  for attribute in mal_email:
    name = attribute['definition']['name']
    if 'domain' in name:
      obs = make_attr_obs(attribute, users, groups, 'DomainName', 'domain', owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif 'hostname'in name:
      obs = make_attr_obs(attribute, users, groups, 'Hostname', 'Hostname_Value', owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif 'ip' in name:
      obs = make_attr_obs(attribute, users, groups, 'Address', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif 'file' in name:
      obs = make_attr_obs(attribute, users, groups, 'file', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif 'email' in name:
      obs = make_attr_obs(attribute, users, groups, 'email', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif 'comment' in name:
      pass
      # TODO
    elif 'hash' in name:
      obs = make_attr_obs(attribute, users, groups, 'file', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'encryption_key':
      notmapped.write('{0} could not be mapped for ioc_redords on new composed observable {1}\n'.format(name, composed_attribute.identifier))
      notmapped.write('{0}\n'.format(json.dumps(attribute)))
    elif name == 'ids_rules':
      obs = make_attr_obs(attribute, users, groups, 'IDSRule', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'analysis_free_text':
      if not report:
        report = make_report(attribute, users, groups, owner, event)
        report.description = ''
      report.description = report.description + '\n' + attribute['value']
      event.reports.append(report)
    elif name == 'yara_rule':
      obs = make_attr_obs(attribute, users, groups, 'IDSRule', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'reference_free_text':
      if not report:
        report = make_report(attribute, users, groups, owner, event)
        report.description = ''
      report.description = report.description + '\n' + attribute['value']
      event.reports.append(report)
    elif 'http' in name:
      obs = make_attr_obs(attribute, users, groups, 'HTTPSession', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif 'traffic_content' in name:
      obs = make_attr_obs(attribute, users, groups, 'forensic_records', 'traffic_content', owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'memory_pattern':
      obs = make_attr_obs(attribute, users, groups, 'Memory', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'mutex':
      obs = make_attr_obs(attribute, users, groups, 'Mutex', 'Mutex_name', owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'win_registry_key':
      value = attribute['value']
      value = value.replace('/', '\\')
      pos = value.find("\\")
      key = value[pos + 1:]
      hive = value[0:pos]
      if hive == 'HKLM' or 'HKEY_LOCAL_MACHINE' in hive:
        hive = 'HKEY_LOCAL_MACHINE'
      elif hive == 'HKCU' or 'HKEY_CURRENT_USER' in hive or hive == 'HCKU':
        hive = 'HKEY_CURRENT_USER'
      elif hive == 'HKEY_CURRENTUSER':
        hive = 'HKEY_CURRENT_USER'
      elif hive == 'HKCR':
        hive = 'HKEY_CLASSES_ROOT'
      else:
        if hive[0:1] == 'H' and hive != 'HKCU_Classes':
          raise Exception('"{0}" not defined'.format(hive))
        else:
          hive = None
      observable = make_observable(attribute, groups, users, event)
      obj = make_object(attribute, observable, groups, users)
      observable.object = obj
      definition = map_obj_def({'name': 'WindowsRegistryKey', 'chksum': None}, obj_defs)
      obj.definition = definition
      if hive:
        attribute['definition']['name'] = 'WindowsRegistryKey_Hive'
        attribute['value'] = hive
        new_attribute = map_attribute(attribute, attr_defs, users, obj, owner, conditions)
        obj.attributes.append(new_attribute)

      attribute['definition']['name'] = 'WindowsRegistryKey_Key'
      attribute['value'] = key
      new_attribute = map_attribute(attribute, attr_defs, users, obj, owner, conditions)
      obj.attributes.append(new_attribute)

      composed_attribute.observables.append(observable)
    elif name == 'vulnerability_cve':
      notmapped.write('{0} could not be mapped for ioc_redords on new composed observable {1}\n'.format(name, composed_attribute.identifier))
      notmapped.write('{0}\n'.format(json.dumps(attribute)))
    elif 'targeted' in name:
      notmapped.write('{0} could not be mapped for ioc_redords on new composed observable {1}\n'.format(name, composed_attribute.identifier))
      notmapped.write('{0}\n'.format(json.dumps(attribute)))
    elif 'observable_location' in name:
      notmapped.write('{0} could not be mapped for ioc_redords on new composed observable {1}\n'.format(name, composed_attribute.identifier))
      notmapped.write('{0}\n'.format(json.dumps(attribute)))
    elif 'password' in name:
      notmapped.write('{0} could not be mapped for ioc_redords on new composed observable {1}\n'.format(name, composed_attribute.identifier))
      notmapped.write('{0}\n'.format(json.dumps(attribute)))
    elif 'traffic_content' in name:
      obs = make_attr_obs(attribute, users, groups, 'forensic_records', 'traffic_content', owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'url':
      obs = make_attr_obs(attribute, users, groups, 'URI', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'url_path':
      # make pattern out of it
      attribute['value'] = u'*{0}'.format(attribute['value'])
      attribute['uuid'] = u'{0}'.format(uuid4())
      attribute['definition']['name'] = 'url_pattern'
      attribute['definition']['chksum'] = None
      obs = make_attr_obs(attribute, users, groups, 'URI', attribute['definition']['name'], owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    elif name == 'url_pattern':
      obs = make_attr_obs(attribute, users, groups, 'URI', name, owner, obj_defs, attr_defs, conditions)
      composed_attribute.observables.append(obs)
    else:
      raise Exception('Mapping for {0} is not defined'.format(name))

  return result_observable


def map_ioc_records(line, users, groups, owner, attr_defs, obj_defs, parent_observable, event, conditions):
  attributes = line['attributes']
  # sort attributes first
  mal_email = list()
  ips = list()
  file_hashes = list()
  domains = list()
  urls = list()
  artifacts = list()
  c2s = list()
  others = list()
  for attribute in attributes:
    name = attribute['definition']['name']
    if 'raw' in name:
      artifacts.append(attribute)
    elif 'c&c' in name:
      c2s.append(attribute)
    elif 'ipv' in name:
      ips.append(attribute)
    elif 'hash' in name:
      file_hashes.append(attribute)
    elif 'email' in name:
      mal_email.append(attribute)
    elif 'domain' in name or 'hostname' in name:
      domains.append(attribute)
    elif 'url' in name:
      urls.append(attribute)
    else:
      others.append(attribute)

  result_observables = list()

  if mal_email:
    observable = map_observable_composition(mal_email, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, 'Malicious E-mail')

    result_observables.append(observable)
    event.indicators.append(indicator)

  if artifacts:
    observable = map_observable_composition(artifacts, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, 'Malware Artifacts')

    result_observables.append(observable)
    event.indicators.append(indicator)

  if ips:
    observable = map_observable_composition(ips, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, 'IP Watchlist')

    result_observables.append(observable)
    event.indicators.append(indicator)

  if file_hashes:
    observable = map_observable_composition(file_hashes, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, 'File Hash Watchlist')

    result_observables.append(observable)
    event.indicators.append(indicator)

  if domains:
    observable = map_observable_composition(domains, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, 'Domain Watchlist')

    result_observables.append(observable)
    event.indicators.append(indicator)

  if c2s:
    observable = map_observable_composition(c2s, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, 'C2')

    result_observables.append(observable)
    event.indicators.append(indicator)

  if urls:
    observable = map_observable_composition(urls, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, 'URL Watchlist')

    result_observables.append(observable)
    event.indicators.append(indicator)

  if others:
    observable = map_observable_composition(others, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, None)

    result_observables.append(observable)
    event.indicators.append(indicator)

  return result_observables


def make_observable(line, groups, users, event):
  result_observable = Observable()
  result_observable.identifier = line['uuid']
  # The creator of the result_observable is the creator of the object
  result_observable.creator_group = groups[line['creator_group_id']]
  result_observable.creator_group_id = result_observable.creator_group.identifier
  result_observable.creator = users[line['creator_id']]
  result_observable.creator_id = result_observable.creator.identifier
  modifier_id = line['modifier_id']
  if modifier_id:
    modifier = users[modifier_id]
  else:
    modifier = result_observable.creator
  result_observable.modifier = modifier
  result_observable.modifier_id = result_observable.modifier.identifier
  result_observable.originating_group = result_observable.creator_group
  result_observable.originating_group_id = result_observable.creator_group.identifier
  result_observable.parent_id = event.identifier
  result_observable.parent = event
  result_observable.event_id = event.identifier
  result_observable.event = event
  # db code is the same as for the object
  result_observable.dbcode = line['dbcode']
  return result_observable


def map_object(parent, line, users, groups, owner, event, attr_defs, obj_defs, conditions):
  definition = line['definition']
  if ['name'] == 'user_account':
    result_observable = make_observable(line, groups, users, event)
    result_observable.identifier = uuid4()

    composed_attribute = ObservableComposition()
    composed_attribute.uuid = line['uuid']
    composed_attribute.dbcode = line['dbcode']

    attributes = line['attributes']
    # create for each a single entry
    for attribute in attributes:
      observable = make_observable(attribute, groups, users, event)
      observable.identifier = uuid4()

      obj = make_object(line, observable, groups, users)
      definition = map_obj_def({'name': 'UserAccount', 'chksum': None}, obj_defs)
      attribtue = map_attribute(attribute, attr_defs, users, obj, owner, conditions)
      obj.attributes.append(attribtue)
      observable.object = obj
      composed_attribute.observables.append(observable)
    result_observable.observable_composition = composed_attribute
    return result_observable
  elif definition['name'] == 'ioc_records':

    result = map_ioc_records(line, users, groups, owner, attr_defs, obj_defs, None, event, conditions)
    if result:
      return result

    # -> composed observable
  elif definition['name'] == 'malicious_website':
    result = map_malicious_website(line, users, groups, owner, attr_defs, obj_defs, event, conditions)
    if result:
      return result
    # -> composed observable
  else:

    observable = make_observable(line, groups, users, event)
    observable.identifier = uuid4()

    obj = map_cybox(line, users, groups, owner, attr_defs, obj_defs, observable, event, conditions)
    if obj:
      observable.object = obj

      return observable

  notmapped.write('Observable could not be created the new event {0}\n'.format(event.identifier))
  notmapped.write('{0}\n'.format(json.dumps(line)))
  return None


def make_reference(attribute, users, groups, report, resources):
  reference = Reference()
  reference.identifier = attribute['uuid']
  resource_id_uuid[attribute['identifier']] = reference.identifier
  reference.creator_group = groups[attribute['creator_group_id']]
  reference.creator_group_id = reference.creator_group.identifier
  reference.creator = users[attribute['creator_id']]
  reference.creator_id = reference.creator.identifier
  modifier_id = attribute.get('modifier_id')
  if modifier_id:
    reference.modifier = users[modifier_id]
  else:
    reference.modifier = reference.creator
  reference.modifier_id = reference.modifier.identifier
  reference.originating_group = reference.creator_group
  reference.originating_group_id = reference.creator_group.identifier

  # TODO definition of report attribute
  definition = map_reference_definition(attribute['definition'], ressources)
  if definition:
    reference.definition = definition
    reference.value = attribute['value']
    parent_id = attribute['attr_parent_id']
    if parent_id:
      parent = attribute_id_uuid.get(parent_id, None)
      # TODO: To check this again!
      if parent:
        parent.children.append(reference)
    return reference
  else:
    notmapped.write('Reference Could not be mapped as definition is missing for the new report {0}\n'.format(report.identifier))
    notmapped.write('{0}\n'.format(json.dumps(line)))
  return None


def make_report(line, users, groups, owner, event):
  report = Report()
  report.creator_group = groups[line['creator_group_id']]
  report.creator_group_id = report.creator_group.identifier
  report.creator = users[line['creator_id']]
  report.creator_id = report.creator.identifier
  modifier_id = line['modifier_id']
  if modifier_id:
    report.modifier = users[modifier_id]
  else:
    report.modifier = report.creator
  report.modifier_id = report.modifier.identifier
  report.originating_group = report.creator_group
  report.originating_group_id = report.creator_group.identifier
  report.event_id = event.identifier
  return report


def map_report(line, users, groups, owner, event, ressources):
  mutexes = list()
  # check if references are not mutexes
  for attribute in line['attributes']:
    if attribute['definition']['name'] == 'mutex':
      mutexes.append(attribute)

  for item in mutexes:
    line['attributes'].remove(item)

  if mutexes:
    observable = map_observable_composition(mutexes, line, users, groups, owner, event)
    indicator = map_indicator(observable, line, users, groups, None)
    event.observables.append(observable)
    event.indicators.append(indicator)

  if line['attributes']:
    # map the remaining to the report
    report = make_report(line, users, groups, owner, event)
    for attribute in line['attributes']:
      if attribute['definition']['name'] == 'comment' or attribute['definition']['name'] == 'description' or attribute['definition']['name'] == 'analysis_free_text' or attribute['definition']['name'] == 'reference_free_text':
        if not report.description:
          report.description = ''
        report.description = report.description + '\n' + attribute['value']
      else:
        reference = make_reference(attribute, users, groups, report, ressources)
        if reference:
          report.references.append(reference)
    return report
  else:
    return None


def map_event(line, users, groups, attr_defs, obj_defs, conditions, ressources):

  event = Event()
  event.identifier = line['uuid']
  event.status_id = line['status_id']
  event.description = line['description']
  event.analysis_id = line['analysis_status_id']

  event.creator_group = groups[line['creator_group_id']]
  event.creator_group_id = event.creator_group.identifier
  event.creator = users[line['creator_id']]
  event.creator_id = event.creator.identifier
  event.dbcode = line['dbcode']
  event.properties.is_shareable = line['published'] == 1
  event.risk_id = line['risk_id']
  event.title = line['title']
  event.modifier = users[line['modifier_id']]
  event.modifier_id = event.modifier.identifier

  event.originating_group = event.creator_group
  event.originating_group_id = event.creator_group.identifier

  for group in line['maingroups']:
    event.groups.append(map_group(group, groups, event.creator))

  for group in line['subgroups']:
    event.groups.append(map_group(group, groups, event.creator))

  for obj in line['objects']:
    definition = obj['definition']
    if 'reference' in definition['name']:
      # TODO map report
      report = map_report(obj, users, groups, event.creator, event, ressources)
      if report:
        event.reports.append(report)
    else:
      observable = map_object(None, obj, users, groups, event.creator, event, attr_defs, obj_defs, conditions)
      if observable:
        if isinstance(observable, ListType):
          for obs in observable:
            event.observables.append(obs)
        else:
          event.observables.append(observable)

  event.last_publish_date = convert_date(line['last_publish_date'])

  convert_date(line['first_seen'])
  convert_date(line['last_seen'])

  event.created_at = convert_date(line['created'])
  event.modified_on = convert_date(line['modified'])
  logger.info('Created event {0}'.format(event))
  return event


session = None


def convert_date(string_date):
  return strings.stringToDateTime(string_date)


if __name__ == '__main__':

  basePath = dirname(abspath(__file__))

  ce1susConfigFile = basePath + '/config/ce1sus.conf'
  config = Configuration(ce1susConfigFile)
  logger = Log(config).get_logger('Main')
  connector = SessionManager(config).connector
  directconnection = connector.get_direct_session()
  session = directconnection
  # Insert groups and keep reference of the group_id and the new uuid
  data_file = open('handlers.txt', 'r')
  lines = data_file.readlines()
  handlers = dict()
  for line in lines:
    handler_dict = json.loads(line)
    id_ = handler_dict['identifier']
    uuid = handler_dict['uuid']
    handlers[id_] = uuid
  data_file.close()

  notmapped = open('notmapped.txt', 'w')

  # check if the handlers are exitsting
  handler_controller = AttributeDefinitionController(config, directconnection)
  temp = dict()
  for key, value in handlers.iteritems():
    try:
      handler = handler_controller.get_handler_by_id(value)
    except ControllerException:
      handler = handler_controller.get_handler_by_id(GenericHandler.get_uuid())
    temp[key] = handler
  # mapped handlers
  handlers = temp

  # insert groups
  group_controller = GroupController(config, directconnection)

  data_file = open('groups.txt', 'r')
  lines = data_file.readlines()
  groups = dict()
  for line in lines:
    group_dict = json.loads(line)
    group = Group()
    id_ = group_dict['identifier']
    group.identifier = group_dict['uuid']
    group.email = group_dict['email']
    group.gpg_key = group_dict['gpg_key']
    group.tlp_lvl = group_dict['tlp_lvl']
    group.name = group_dict['name']
    group.send_usermails = group_dict['usermails']

    if group_dict['can_download'] == 1:
      group.permissions.can_download = True
    else:
      group.permissions.can_download = False

    # Setting not available in previous version
    group.permissions.propagate_tlp = False

    group.description = group_dict['description']
    try:
      group_controller.insert_group(group, commit=False)
    except:
      group = group_controller.get_group_by_id(group.identifier)

    groups[id_] = group
  data_file.close()

  # insert users
  user_controller = UserController(config, directconnection)

  data_file = open('users.txt', 'r')
  lines = data_file.readlines()
  users = dict()
  for line in lines:
    user_dict = json.loads(line)
    user = User()
    id_ = user_dict['identifier']

    user.username = user_dict['username']
    user.activation_str = user_dict['activation_str']

    dbcode = user_dict['dbcode']
    bitright = BitRight(dbcode)

    user.permissions.manage_group = bitright.set_group
    # The same as in the old one
    user.permissions.validate = bitright.privileged
    user.permissions.privileged = bitright.privileged

    user.activated = convert_date(user_dict['activated'])
    disabled = user_dict['disabled']
    if disabled == 1:
      user.permissions.disabled = True
    else:
      user.permissions.disabled = False

    user.activation_sent = user_dict['activation_sent']
    user.gpg_key = user_dict['gpg_key']
    user.password = user_dict['password']
    group_id = user_dict['group_id']
    user.group = groups[group_id]
    user.group_id = user.group.identifier

    user.name = user_dict['name']
    user.sirname = user_dict['sirname']

    user.last_login = convert_date(user_dict['last_login'])

    user.api_key = user_dict['api_key']
    user.email = user_dict['email']

    try:
      user_controller.insert_user(user, commit=False)
    except ControllerIntegrityException as error:
      print u'{0}'.format(error)
      user = user_controller.get_user_by_username(user.username)

    users[id_] = user
  data_file.close()

  event_controller = EventController(config, directconnection)

  def_con = AttributeDefinitionController(config, directconnection)
  attr_defs = def_con.get_all_attribute_definitions()
  def_con = ObjectDefinitionController(config, directconnection)
  obj_defs = def_con.get_all_object_definitions()
  def_con = ConditionController(config, directconnection)
  conditions = def_con.get_all_conditions()
  def_con = ReferencesController(config, directconnection)
  ressources = def_con.get_all()
  def_con = IndicatorController(config, directconnection)
  types = def_con.get_all()

  data_file = open('events.txt', 'r')
  lines = data_file.readlines()
  for line in lines:
    json_dict = json.loads(line)
    if json_dict['identifier'] not in [41, 211]:
      event = map_event(json_dict, users, groups, attr_defs, obj_defs, conditions, ressources)
      event_controller.event_broker.insert(event, False)

  data_file.close()

  notmapped.close()
  # event_controller.event_broker.do_commit(True)
  directconnection.close()



